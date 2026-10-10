// TITP Chinese Font Fix - BepInEx 5 plugin (v6)
// The game's TMP font assets are static and contain no CJK glyphs, so the Chinese
// translations that are already injected into TMP_Text components render as tofu.
//
// v5 approach:
//   1. Build a dynamic CJK TMP_FontAsset at runtime from the legacy Font asset that
//      inject.py re-pointed at CJK OS fonts (TMP_FontAsset.CreateFontAsset - works).
//   2. Pre-populate it with every CJK character used by the loaded TMP texts and
//      TextAssets (the whole localisation dictionary).
//   3. Wire the atlas texture into the material, register the asset as a fallback
//      everywhere, and force a mesh rebuild.
//   4. For any text that still cannot show CJK after the fallback route, point that
//      text straight at the CJK asset.
//
// v6 additions (hardcoded UI strings that are NOT in the localisation assets):
//   5. "Census": dump every distinct string rendered by TMP_Text / UnityEngine.UI.Text
//      into BepInEx\plugins\TITP-CHS\ui_strings.txt (path<TAB>text) so the untranslated
//      hardcoded labels can be identified.
//   6. "Overlay": if BepInEx\plugins\TITP-CHS\ui_extra.tsv exists (english<TAB>chinese per
//      line), any text component whose text matches exactly is rewritten at runtime.
//
// v8 addition (vanilla crash guard):
//   7. ConditionHelper eagerly dereferences GameHandler.CurrentEventProcessor while
//      evaluating some event conditions (e.g. "REQUEST_AGING: >=5"), so when no event
//      processor is active (the Applications window opens a micromonologue popup) the
//      condition lambda throws NullReferenceException. That aborts
//      EventProcessor.GetFirstMicromonologueLine() -> MicroMonologueElement.Initialize()
//      halfway, leaving the accept/decline popup visible but dead (this is the
//      "hire screen stuck on Yes/No" bug). A Harmony finalizer on
//      ThisIsThePresident.Game.ConditionPostfixListElement.GetChar() turns any such
//      exception into a plain "false" result, so condition evaluation continues.
//
// Compile with plugin\build_plugin.ps1 (system csc, C# 5 only).
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Text;
using BepInEx;
using BepInEx.Logging;
using HarmonyLib;
using TMPro;
using UnityEngine;
using UnityEngine.TextCore;
using UnityEngine.TextCore.LowLevel;
using UnityEngine.UI;

namespace TITP
{
    [BepInPlugin("titp.chinesefontfix", "TITP Chinese Font Fix", "8.0.0")]
    public class TITPFontFix : BaseUnityPlugin
    {
        private const int SamplingPointSize = 48;
        private const int Padding = 6;
        private const int AtlasSize = 4096;

        private TMP_FontAsset _cjk;
        private readonly HashSet<char> _added = new HashSet<char>();
        private readonly HashSet<int> _handled = new HashSet<int>();
        private int _frame;
        private int _bakeTries;
        private int _forced;
        private int _reports;
        private int _lastGrow = -100000;

        // v6 state
        private string _dataDir;
        private readonly Dictionary<string, string> _uiMap = new Dictionary<string, string>();
        private readonly Dictionary<string, string> _uiMapTrim = new Dictionary<string, string>();
        private int _clears;
        private readonly Dictionary<string, string> _census = new Dictionary<string, string>();
        private int _replaced;
        private int _censusWrites;
        private int _lastCensusWrite = -100000;

        void Awake()
        {
            _dataDir = Path.Combine(Paths.PluginPath, "TITP-CHS");
            try { if (!Directory.Exists(_dataDir)) Directory.CreateDirectory(_dataDir); }
            catch (Exception ex) { Logger.LogWarning("TITP font fix: cannot create data dir: " + ex.Message); }
            LoadUiMap();
            InstallConditionGuard();
            Logger.LogInfo("TITP font fix v8: unity=" + Application.unityVersion + " pluginPath=" + Paths.PluginPath
                + " dataDir=" + _dataDir + " uiMap=" + _uiMap.Count);
        }

        // ------------------------------------------------------------------
        // v8: keep the game alive when an event condition throws (vanilla bug)
        // ------------------------------------------------------------------
        private static string _curCondition;
        private static int _condGuardErrors;
        private static PropertyInfo _cepProp;
        private static ManualLogSource _log;

        private static void LogWarn(string message)
        {
            if (_log != null) _log.LogWarning(message);
        }

        private void InstallConditionGuard()
        {
            _log = Logger;
            try
            {
                Harmony harmony = new Harmony("titp.chinesefontfix.conditionguard");
                MethodInfo getChar = AccessTools.Method("ThisIsThePresident.Game.ConditionPostfixListElement:GetChar");
                if (getChar == null)
                {
                    Logger.LogWarning("condition guard: ConditionPostfixListElement.GetChar not found");
                }
                else
                {
                    MethodInfo fin = typeof(TITPFontFix).GetMethod("ConditionGetCharFinalizer",
                        BindingFlags.Static | BindingFlags.NonPublic);
                    harmony.Patch(getChar, finalizer: new HarmonyMethod(fin));
                    Logger.LogInfo("condition guard: finalizer installed on "
                        + getChar.DeclaringType.FullName + "." + getChar.Name);
                }
                MethodInfo solve = AccessTools.Method("ThisIsThePresident.Game.ConditionHelper:SolveCondition",
                    new Type[] { typeof(string), typeof(bool) });
                if (solve != null)
                {
                    MethodInfo pre = typeof(TITPFontFix).GetMethod("ConditionSolvePrefix",
                        BindingFlags.Static | BindingFlags.NonPublic);
                    harmony.Patch(solve, prefix: new HarmonyMethod(pre));
                }
                else
                {
                    Logger.LogWarning("condition guard: ConditionHelper.SolveCondition not found (no breadcrumb)");
                }
            }
            catch (Exception ex)
            {
                Logger.LogWarning("condition guard: install failed: " + ex);
            }
        }

        // Remember the condition being evaluated so the log names the culprit.
        private static void ConditionSolvePrefix(string condition)
        {
            _curCondition = condition;
        }

        // Any exception inside a condition function is reported as "condition not met"
        // instead of aborting the caller (EventProcessor.GetFirstMicromonologueLine etc).
        private static Exception ConditionGetCharFinalizer(Exception __exception, ref char __result)
        {
            if (__exception == null) return null;
            _condGuardErrors++;
            if (_condGuardErrors <= 20)
            {
                string where = "";
                try { where = DescribeCurrentEventProcessor(); }
                catch (Exception ex) { where = " cep=? (" + ex.GetType().Name + ")"; }
                LogWarn("condition guard #" + _condGuardErrors + ": '" + (_curCondition == null ? "?" : _curCondition)
                    + "' threw " + __exception.GetType().Name + ": " + __exception.Message + where + " -> treated as false");            }
            __result = 'f';
            return null;
        }

        private static string DescribeCurrentEventProcessor()
        {
            if (_cepProp == null)
            {
                Assembly[] asms = AppDomain.CurrentDomain.GetAssemblies();
                for (int i = 0; i < asms.Length; i++)
                {
                    Type gh = asms[i].GetType("ThisIsThePresident.GameHandler", false);
                    if (gh == null) continue;
                    _cepProp = gh.GetProperty("CurrentEventProcessor", BindingFlags.Public | BindingFlags.Static);
                    if (_cepProp != null) break;
                }
            }
            if (_cepProp == null) return " cep=?";
            object ep = _cepProp.GetValue(null, null);
            if (ep == null) return " cep=null";
            PropertyInfo info = ep.GetType().GetProperty("Info", BindingFlags.Public | BindingFlags.Instance);
            object infoVal = info == null ? null : info.GetValue(ep, null);
            return " cep=set info=" + (infoVal == null ? "null" : "set");
        }

        void Update()
        {
            _frame++;
            if (_frame < 45) return;

            if (_cjk == null)
            {
                if (_frame % 45 != 0) return;
                _bakeTries++;
                _cjk = Bake();
                if (_cjk == null)
                {
                    if (_bakeTries > 25)
                    {
                        Logger.LogError("TITP font fix: unable to build a CJK font asset, giving up");
                        enabled = false;
                    }
                    return;
                }
            }

            if (_frame % 30 == 0)
            {
                RegisterAll();
                RefreshTexts(80);
                ReplaceUiTexts();
            }

            if (_frame % 120 == 0) Census();
            if (_frame - _lastCensusWrite > 1500) WriteCensus();

            if (_frame % 600 == 0) Report();
            if (_frame - _lastGrow > 900) Grow();
        }

        // ------------------------------------------------------- v6: hardcoded UI overlay

        private void LoadUiMap()
        {
            if (_dataDir == null) return;
            string p = Path.Combine(_dataDir, "ui_extra.tsv");
            if (!File.Exists(p)) return;
            try
            {
                string[] lines = File.ReadAllLines(p, Encoding.UTF8);
                for (int i = 0; i < lines.Length; i++)
                {
                    string line = lines[i];
                    if (line == null) continue;
                    if (line.Length == 0 || line[0] == '#') continue;
                    int tab = line.IndexOf('\t');
                    if (tab <= 0) continue;
                    string en = Unescape(line.Substring(0, tab));
                    string zh = Unescape(line.Substring(tab + 1));
                    if (zh == "<clear>") { zh = ""; _clears++; }
                    if (!_uiMap.ContainsKey(en)) _uiMap.Add(en, zh);
                    string en2 = en.Trim();
                    if (en2.Length > 0 && !_uiMapTrim.ContainsKey(en2)) _uiMapTrim.Add(en2, zh);
                }
                Logger.LogInfo("TITP font fix: ui_extra.tsv loaded, " + _uiMap.Count + " entries (" + _clears + " clears, trimmed index " + _uiMapTrim.Count + ")");
            }
            catch (Exception ex) { Logger.LogWarning("TITP font fix: ui_extra.tsv read failed: " + ex.Message); }
        }

        private string Unescape(string s)
        {
            if (s.IndexOf('\\') < 0) return s;
            return s.Replace("\\r\\n", "\n").Replace("\\n", "\n").Replace("\\r", "\n").Replace("\\t", "\t");
        }

        private void ReplaceUiTexts()
        {
            if (_uiMap.Count == 0) return;
            TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
            for (int i = 0; i < texts.Length; i++)
            {
                TMP_Text t = texts[i];
                if (t == null) continue;
                string s = t.text;
                if (string.IsNullOrEmpty(s)) continue;
                string repl;
                if (!_uiMap.TryGetValue(s, out repl))
                {
                    string trimmed = s.Trim();
                    if (trimmed.Length == 0 || !_uiMapTrim.TryGetValue(trimmed, out repl)) continue;
                }
                try
                {
                    t.text = repl;
                    t.ForceMeshUpdate();
                    _replaced++;
                    Logger.LogInfo("TITP font fix: ui overlay '" + s + "' -> '" + repl + "' on " + NodePath(t));
                }
                catch (Exception ex) { Logger.LogWarning("TITP font fix: ui overlay failed: " + ex.Message); }
            }

            Text[] legacy = Resources.FindObjectsOfTypeAll<Text>();
            for (int i = 0; i < legacy.Length; i++)
            {
                Text t = legacy[i];
                if (t == null) continue;
                string s = t.text;
                if (string.IsNullOrEmpty(s)) continue;
                string repl;
                if (!_uiMap.TryGetValue(s, out repl))
                {
                    string trimmed = s.Trim();
                    if (trimmed.Length == 0 || !_uiMapTrim.TryGetValue(trimmed, out repl)) continue;
                }
                try { t.text = repl; _replaced++; }
                catch (Exception) { }
            }
        }

        // ------------------------------------------------------- v6: string census

        private void Census()
        {
            TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
            for (int i = 0; i < texts.Length; i++)
            {
                TMP_Text t = texts[i];
                if (t == null) continue;
                string s = t.text;
                if (string.IsNullOrEmpty(s)) continue;
                if (!_census.ContainsKey(s)) _census.Add(s, NodePath(t));
            }
            Text[] legacy = Resources.FindObjectsOfTypeAll<Text>();
            for (int i = 0; i < legacy.Length; i++)
            {
                Text t = legacy[i];
                if (t == null) continue;
                string s = t.text;
                if (string.IsNullOrEmpty(s)) continue;
                if (!_census.ContainsKey(s)) _census.Add(s, "UI.Text:" + NodePath(t));
            }
        }

        private void WriteCensus()
        {
            if (_dataDir == null || _census.Count == 0) return;
            _lastCensusWrite = _frame;
            try
            {
                List<string> lines = new List<string>(_census.Count);
                foreach (KeyValuePair<string, string> kv in _census)
                {
                    string s = kv.Key.Replace("\r", "\\r").Replace("\n", "\\n").Replace("\t", "\\t");
                    lines.Add(kv.Value + "\t" + s);
                }
                lines.Sort();
                File.WriteAllLines(Path.Combine(_dataDir, "ui_strings.txt"), lines.ToArray(), Encoding.UTF8);
                _censusWrites++;
                Logger.LogInfo("TITP font fix: census written #" + _censusWrites + " distinct=" + _census.Count
                    + " replaced=" + _replaced);
            }
            catch (Exception ex) { Logger.LogWarning("TITP font fix: census write failed: " + ex.Message); }
        }

        // ------------------------------------------------------------------ baking

        private TMP_FontAsset Bake()
        {
            Font src = FindCjkCapableFont();
            if (src == null)
            {
                Logger.LogWarning("TITP font fix: no CJK-capable legacy Font asset loaded yet");
                return null;
            }

            TMP_FontAsset fa = null;
            try
            {
                fa = TMP_FontAsset.CreateFontAsset(src, SamplingPointSize, Padding, GlyphRenderMode.SDFAA,
                    AtlasSize, AtlasSize, AtlasPopulationMode.Dynamic, true);
            }
            catch (Exception ex)
            {
                Logger.LogWarning("TITP font fix: CreateFontAsset threw " + ex.GetType().Name + ": " + ex.Message);
                return null;
            }
            if (fa == null)
            {
                Logger.LogWarning("TITP font fix: CreateFontAsset('" + src.name + "') returned null");
                return null;
            }
            fa.name = "TITP-CJK";
            Logger.LogInfo("TITP font fix: baked '" + fa.name + "' from legacy Font '" + src.name
                + "' (fallbackNames=" + Join(fontNamesOf(src)) + ")");

            HashSet<char> want = CollectChars();
            _added.Clear();
            string missing = "";
            bool ok = false;
            try { ok = fa.TryAddCharacters(CharsOf(want), out missing); }
            catch (Exception ex) { Logger.LogWarning("TITP font fix: TryAddCharacters threw " + ex.Message); }
            Logger.LogInfo("TITP font fix: bake wanted=" + want.Count + " ok=" + ok
                + " missingCount=" + missing.Length + " glyphs=" + Count(fa.glyphTable)
                + " chars=" + Count(fa.characterTable));
            if (missing.Length > 0 && missing.Length < 80) Logger.LogInfo("TITP font fix: missing glyphs: " + missing);

            foreach (char c in want) _added.Add(c);
            PostProcess(fa);
            return fa;
        }

        private void Grow()
        {
            if (_cjk == null) return;
            _lastGrow = _frame;
            HashSet<char> want = CollectChars();
            List<char> fresh = new List<char>();
            foreach (char c in want) if (!_added.Contains(c)) fresh.Add(c);
            if (fresh.Count == 0) return;
            string missing = "";
            bool ok = false;
            try { ok = _cjk.TryAddCharacters(new string(fresh.ToArray()), out missing); }
            catch (Exception ex) { Logger.LogWarning("TITP font fix: grow threw " + ex.Message); }
            for (int i = 0; i < fresh.Count; i++) _added.Add(fresh[i]);
            Logger.LogInfo("TITP font fix: grow +" + fresh.Count + " chars ok=" + ok + " glyphs=" + Count(_cjk.glyphTable)
                + " chars=" + Count(_cjk.characterTable));
            PostProcess(_cjk);
            _handled.Clear();   // force a full re-render pass
        }

        // Wire the (possibly newly grown) atlas texture into the material and refresh
        // TMP's internal tables.
        private void PostProcess(TMP_FontAsset fa)
        {
            try
            {
                MethodInfo mi = typeof(TMP_FontAsset).GetMethod("UpdateAtlasTexture",
                    BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                if (mi != null) mi.Invoke(fa, null);
            }
            catch (Exception ex) { Logger.LogWarning("TITP font fix: UpdateAtlasTexture failed: " + ex.Message); }

            Texture2D tex = null;
            if (fa.atlasTextures != null && fa.atlasTextures.Length > 0) tex = fa.atlasTextures[0];
            Logger.LogInfo("TITP font fix: atlas count=" + (fa.atlasTextures == null ? 0 : fa.atlasTextures.Length)
                + " atlas0=" + (tex == null ? "null" : tex.width + "x" + tex.height + "/" + tex.format)
                + " material=" + (fa.material == null ? "null" : fa.material.shader.name));
            if (fa.material != null && tex != null)
            {
                fa.material.SetTexture("_MainTex", tex);
                fa.material.SetFloat("_TextureWidth", tex.width);
                fa.material.SetFloat("_TextureHeight", tex.height);
                fa.material.SetFloat("_GradientScale", Padding + 1);
            }
        }

        private Font FindCjkCapableFont()
        {
            Font[] fonts = Resources.FindObjectsOfTypeAll<Font>();
            Font best = null;
            int bestScore = -1;
            for (int i = 0; i < fonts.Length; i++)
            {
                Font f = fonts[i];
                if (f == null) continue;
                string[] names = fontNamesOf(f);
                int score = 0;
                for (int k = 0; k < names.Length; k++)
                {
                    string n = names[k].ToLowerInvariant();
                    if (n.IndexOf("yahei") >= 0 || n.IndexOf("simhei") >= 0 || n.IndexOf("simsun") >= 0
                        || n.IndexOf("noto sans sc") >= 0 || n.IndexOf("source han") >= 0 || n.IndexOf("dengxian") >= 0)
                        score += 10;
                }
                Logger.LogInfo("TITP font fix: candidate Font '" + f.name + "' names=[" + Join(names) + "] score=" + score);
                if (score > bestScore) { bestScore = score; best = f; }
            }
            if (best == null || bestScore <= 0) return null;
            return best;
        }

        private static string[] fontNamesOf(Font f)
        {
            try { return f.fontNames == null ? new string[0] : f.fontNames; }
            catch (Exception) { return new string[0]; }
        }

        private static string Join(string[] a)
        {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < a.Length; i++) { if (i > 0) sb.Append(","); sb.Append(a[i]); }
            return sb.ToString();
        }

        // ------------------------------------------------------------------ character collection

        private HashSet<char> CollectChars()
        {
            HashSet<char> want = new HashSet<char>();
            TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
            for (int i = 0; i < texts.Length; i++)
            {
                if (texts[i] == null) continue;
                AddCjk(texts[i].text, want);
            }
            TextAsset[] assets = Resources.FindObjectsOfTypeAll<TextAsset>();
            for (int i = 0; i < assets.Length; i++)
            {
                if (assets[i] == null) continue;
                try { AddCjk(assets[i].text, want); } catch (Exception) { }
            }
            return want;
        }

        private static void AddCjk(string s, HashSet<char> set)
        {
            if (string.IsNullOrEmpty(s)) return;
            for (int i = 0; i < s.Length; i++) if (IsCJK(s[i])) set.Add(s[i]);
        }

        private static string CharsOf(HashSet<char> set)
        {
            StringBuilder sb = new StringBuilder(set.Count);
            foreach (char c in set) sb.Append(c);
            return sb.ToString();
        }

        // ------------------------------------------------------------------ registration

        private void RegisterAll()
        {
            if (_cjk == null) return;
            List<TMP_FontAsset> settings = null;
            try { settings = TMP_Settings.fallbackFontAssets; } catch (Exception) { }
            if (settings != null && !settings.Contains(_cjk)) settings.Insert(0, _cjk);

            TMP_FontAsset[] all = Resources.FindObjectsOfTypeAll<TMP_FontAsset>();
            for (int i = 0; i < all.Length; i++)
            {
                TMP_FontAsset fa = all[i];
                if (fa == null || fa == _cjk) continue;
                List<TMP_FontAsset> table = null;
                try { table = fa.fallbackFontAssetTable; } catch (Exception) { continue; }
                if (table == null)
                {
                    table = new List<TMP_FontAsset>();
                    try { fa.fallbackFontAssetTable = table; } catch (Exception) { continue; }
                }
                if (!table.Contains(_cjk)) table.Add(_cjk);
            }
        }

        private void RefreshTexts(int maxPerCall)
        {
            TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
            int done = 0;
            for (int i = 0; i < texts.Length && done < maxPerCall; i++)
            {
                TMP_Text t = texts[i];
                if (t == null) continue;
                if (!t.gameObject.activeInHierarchy) continue;
                int id = t.GetInstanceID();
                if (_handled.Contains(id)) continue;
                string s = t.text;
                if (string.IsNullOrEmpty(s) || !HasCJK(s)) { _handled.Add(id); continue; }
                _handled.Add(id);
                done++;
                try { t.ForceMeshUpdate(); } catch (Exception) { }
                int visible = VisibleCjk(t);
                if (visible > 0) continue;
                // fallback route did not work for this text - point it at the CJK asset
                try
                {
                    t.font = _cjk;
                    t.fontSharedMaterial = _cjk.material;
                    t.ForceMeshUpdate();
                    _forced++;
                    visible = VisibleCjk(t);
                    Logger.LogInfo("TITP font fix: forced CJK font on " + NodePath(t) + " visible=" + visible);
                }
                catch (Exception ex) { Logger.LogWarning("TITP font fix: force font on " + NodePath(t) + " failed: " + ex.Message); }
            }
        }

        private static int VisibleCjk(TMP_Text t)
        {
            TMP_TextInfo ti = t.textInfo;
            if (ti == null || ti.characterInfo == null) return 0;
            int vis = 0;
            for (int i = 0; i < ti.characterCount && i < ti.characterInfo.Length; i++)
                if (IsCJK(ti.characterInfo[i].character) && ti.characterInfo[i].isVisible) vis++;
            return vis;
        }

        private void Report()
        {
            _reports++;
            if (_cjk == null) return;
            HashSet<char> want = CollectChars();
            int pending = 0;
            foreach (char c in want) if (!_added.Contains(c)) pending++;
            TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
            int activeCjk = 0, cjkChars = 0, cjkVisible = 0;
            string sample = "";
            for (int i = 0; i < texts.Length; i++)
            {
                TMP_Text t = texts[i];
                if (t == null || !t.gameObject.activeInHierarchy) continue;
                string s = t.text;
                if (string.IsNullOrEmpty(s) || !HasCJK(s)) continue;
                activeCjk++;
                TMP_TextInfo ti = t.textInfo;
                if (ti == null || ti.characterInfo == null) continue;
                int vis = 0;
                for (int c = 0; c < ti.characterCount && c < ti.characterInfo.Length; c++)
                    if (IsCJK(ti.characterInfo[c].character)) { cjkChars++; if (ti.characterInfo[c].isVisible) { cjkVisible++; vis++; } }
                if (sample.Length == 0 && vis > 0)
                    sample = NodePath(t) + " font=" + (t.font == null ? "null" : t.font.name) + " '" + s + "'";
            }
            Logger.LogInfo("TITP font fix SUMMARY #" + _reports + ": assetChars=" + Count(_cjk.characterTable)
                + " known=" + _added.Count + " pending=" + pending + " forced=" + _forced
                + " activeCjkTexts=" + activeCjk + " cjkChars=" + cjkChars + " cjkVisible=" + cjkVisible
                + " census=" + _census.Count + " uiReplaced=" + _replaced
                + (sample.Length > 0 ? " | " + sample : ""));
        }

        // ------------------------------------------------------------------ helpers

        private static bool IsCJK(char c)
        {
            return (c >= 0x2E80 && c <= 0x9FFF) || (c >= 0xF900 && c <= 0xFAFF) || (c >= 0xFF00 && c <= 0xFFEF);
        }

        private static bool HasCJK(string s)
        {
            for (int i = 0; i < s.Length; i++) if (IsCJK(s[i])) return true;
            return false;
        }

        private static int Count<T>(List<T> list) { return list == null ? -1 : list.Count; }

        private static string NodePath(Component c)
        {
            if (c == null) return "(null)";
            StringBuilder sb = new StringBuilder(c.name);
            Transform p = c.transform.parent;
            int guard = 0;
            while (p != null && guard++ < 6) { sb.Insert(0, p.name + "/"); p = p.parent; }
            return sb.ToString();
        }
    }
}
