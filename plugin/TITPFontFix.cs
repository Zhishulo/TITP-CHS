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
// v8.1 addition (second half of the same vanilla bug):
//   8. Treating a thrown condition as plain "false" is not enough: the micromonologue data
//      contains mutually exclusive lines such as "REQUEST_AGING: >=5" and "REQUEST_AGING: <5",
//      and making BOTH false leaves no matching line at all, so
//      EventProcessor.GetFirstMicromonologueLine() runs past the end of the line array
//      (IndexOutOfRangeException) and the popup stays dead. v8.1 therefore wraps every entry
//      of ConditionHelper.conditionFunctions: when the original function throws, the unknown
//      quantity is treated as 0 and the comparison (">=5", "<5", ...) is re-evaluated against
//      it, mirroring ConditionHelper.CompareInt. The two branches stay complementary, exactly
//      one line matches, and the value is semantically right (a freshly approached character
//      has no accumulated request bar yet).
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
    [BepInPlugin("titp.chinesefontfix", "TITP Chinese Font Fix", "8.1.0")]
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
            InstallHireFix();
            Logger.LogInfo("TITP font fix v8.3: unity=" + Application.unityVersion + " pluginPath=" + Paths.PluginPath
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
                WrapConditionFunctions();
            }
            catch (Exception ex)
            {
                Logger.LogWarning("condition guard: install failed: " + ex);
            }
        }

        // ------------------------------------------------------------------ v8.3
        // Vanilla bug: when a micromonologue option leads straight to a result page
        // ("immediate result"), MicroMonologuePanel.OnElementClosing creates a second
        // MicroMonologueElement for that result page, but only copies SelectedOption --
        // not the accepted flag. MicroMonologueElement.Initialize then re-derives
        // 'accepted' from EventProcessor.GetCurrentLine(), which after FollowChoice()
        // points at the REJECT line, so the result page always reports accepted=false.
        // MicroMonologueElement.CloseClicked() therefore calls the hiring callback with
        // result=false and ApplicationsWindow.OnHire never runs Hire(slot): the candidate
        // is never added to the team (salary/event effects do apply, which is why the
        // popup looks like it worked).
        // Fix: remember the accepted flag of the element the player actually clicked and
        // restore it on the result page right before CloseClicked() reads it.
        private static bool? _pendingImmediateAccepted;

        private void InstallHireFix()
        {
            try
            {
                Harmony harmony = new Harmony("titp.chinesefontfix.hirefix");
                PatchPrefix(harmony, "ThisIsThePresident.UI.MicroMonologuePanel:OnElementClosing", "RecordAcceptancePrefix");
                PatchPrefix(harmony, "ThisIsThePresident.MicroMonologueElement:CloseClicked", "ApplyAcceptancePrefix");
            }
            catch (Exception ex)
            {
                Logger.LogWarning("hire fix: install failed: " + ex);
            }
        }

        private void PatchPrefix(Harmony harmony, string target, string prefixName)
        {
            try
            {
                MethodInfo m = AccessTools.Method(target);
                if (m == null)
                {
                    Logger.LogWarning("hire fix: " + target + " not found");
                    return;
                }
                MethodInfo pre = typeof(TITPFontFix).GetMethod(prefixName, BindingFlags.Static | BindingFlags.NonPublic);
                harmony.Patch(m, prefix: new HarmonyMethod(pre));
                Logger.LogInfo("hire fix: patched " + target);
            }
            catch (Exception ex)
            {
                Logger.LogWarning("hire fix: cannot patch " + target + ": " + ex.Message);
            }
        }

        private static object GetMember(object o, string name)
        {
            if (o == null) return null;
            Type t = o.GetType();
            PropertyInfo p = t.GetProperty(name, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
            if (p != null) return p.GetValue(o, null);
            FieldInfo f = t.GetField(name, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
            return f == null ? null : f.GetValue(o);
        }

        private static void RecordAcceptancePrefix(object __instance, bool isAccepted, bool hasImmediateResult)
        {
            if (!hasImmediateResult) return;
            try
            {
                object top = PeekTop(GetMember(__instance, "backDrops"));
                object acc = top == null ? null : GetMember(top, "accepted");
                if (acc is bool)
                {
                    _pendingImmediateAccepted = (bool)acc;
                }
            }
            catch (Exception ex)
            {
                LogWarn("hire fix: cannot record accepted flag: " + ex.Message);
            }
        }

        private static void ApplyAcceptancePrefix(object __instance)
        {
            try
            {
                if (!_pendingImmediateAccepted.HasValue) return;
                object isResult = GetMember(__instance, "isResult");
                if (!(isResult is bool) || !(bool)isResult) return;
                bool want = _pendingImmediateAccepted.Value;
                _pendingImmediateAccepted = null;
                SetMember(__instance, "accepted", want);
            }
            catch (Exception ex)
            {
                LogWarn("hire fix: cannot restore accepted flag: " + ex.Message);
            }
        }

        private static object PeekTop(object collection)
        {
            if (collection == null) return null;
            object v = InvokeMethod(collection, "Peek");
            if (v != null) return v;
            return InvokeMethod(collection, "get_Item", 0);
        }

        private static object InvokeMethod(object target, string name, params object[] args)
        {
            if (target == null) return null;
            Type t = target.GetType();
            MethodInfo m = args.Length == 0
                ? t.GetMethod(name, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
                : t.GetMethod(name, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance,
                    null, Array.ConvertAll(args, a => a.GetType()), null);
            return m == null ? null : m.Invoke(target, args);
        }

        private static void SetMember(object o, string name, object value)
        {
            if (o == null) return;
            Type t = o.GetType();
            FieldInfo f = t.GetField(name, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
            if (f != null)
            {
                f.SetValue(o, value);
                return;
            }
            PropertyInfo p = t.GetProperty(name, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
            if (p != null && p.CanWrite) p.SetValue(o, value, null);
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

        // ---------------------------------------------------------------- v8.1
        // If a condition function throws (it dereferences the inactive global event
        // processor) we must not simply answer "false": the data uses mutually exclusive
        // pairs like "REQUEST_AGING: >=5" / "REQUEST_AGING: <5", and making both false
        // leaves EventProcessor.GetFirstMicromonologueLine() with no matching line at all
        // (it then throws IndexOutOfRangeException and the popup stays dead).
        // Instead the unknown quantity is treated as 0 and the comparison is evaluated
        // again - exactly one branch of such a pair then matches.
        private static int _condFallbacks;
        private static int _condWrapped;

        private void WrapConditionFunctions()
        {
            try
            {
                // Dictionary<string, Func<string[], bool>> on ConditionHelper. The condition
                // element looks the delegate up lazily, so replacing the entries also takes
                // effect for elements that were created earlier.
                FieldInfo fld = null;
                Type helper = AccessTools.TypeByName("ThisIsThePresident.Game.ConditionHelper");
                if (helper != null)
                {
                    fld = helper.GetField("conditionFunctions",
                        BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public);
                }
                IDictionary dict = (fld == null) ? null : (fld.GetValue(null) as IDictionary);
                if (dict == null)
                {
                    Logger.LogWarning("condition guard: ConditionHelper.conditionFunctions not found");
                    return;
                }
                // snapshot the keys first - the dictionary must not be modified while enumerating
                List<object> keys = new List<object>();
                foreach (object k in dict.Keys) keys.Add(k);
                int wrapped = 0;
                int nulls = 0;
                for (int i = 0; i < keys.Count; i++)
                {
                    string key = keys[i] as string;
                    if (key == null) continue;
                    object raw = dict[keys[i]];
                    Func<string[], bool> original = raw as Func<string[], bool>;
                    if (raw != null && original == null)
                    {
                        Logger.LogWarning("condition guard: " + key + " is not Func<string[],bool>");
                        continue;
                    }
                    // "LOBBIED" ships as a null entry in the vanilla dictionary; calling it
                    // would throw NullReferenceException, so give it the same fallback.
                    if (original == null) nulls++;
                    dict[keys[i]] = WrapConditionFunction(key, original);
                    wrapped++;
                }
                _condWrapped = wrapped;
                Logger.LogInfo("condition guard: wrapped " + wrapped + " of " + keys.Count
                    + " condition functions with a value-based fallback (" + nulls + " were null)");
            }
            catch (Exception ex)
            {
                Logger.LogWarning("condition guard: wrapping condition functions failed: " + ex);
            }
        }

        private static Func<string[], bool> WrapConditionFunction(string key, Func<string[], bool> original)
        {
            return delegate(string[] parts)
            {
                if (original == null) return FallbackConditionValue(parts);
                try
                {
                    return original(parts);
                }
                catch (Exception ex)
                {
                    _condFallbacks++;
                    bool result = FallbackConditionValue(parts);
                    if (_condFallbacks <= 20)
                    {
                        LogWarn("condition value guard #" + _condFallbacks + ": " + key + " '"
                            + (_curCondition == null ? "?" : _curCondition) + "' threw "
                            + ex.GetType().Name + ": " + ex.Message + " -> quantity assumed 0 -> "
                            + (result ? "true" : "false"));
                    }
                    return result;
                }
            };
        }

        // parts[1] is the comparison written in the data, e.g. ">=5" or "<5".
        private static bool FallbackConditionValue(string[] parts)
        {
            if (parts == null || parts.Length < 2) return false;
            return CompareAssumedZero(parts[1]);
        }

        // Mirror of ConditionHelper.CompareInt(conditionPart, 0) - the mirrors the game's own
        // order of comparison operations (==, !=, >=, <=, >, <), with the unknown quantity
        // taken as 0 because nothing has accumulated yet.
        private static bool CompareAssumedZero(string spec)
        {
            if (string.IsNullOrEmpty(spec)) return false;
            spec = spec.Trim();
            string[] operators = new string[6] { "==", "!=", ">=", "<=", ">", "<" };
            for (int i = 0; i < operators.Length; i++)
            {
                if (!spec.StartsWith(operators[i], StringComparison.Ordinal)) continue;
                int limit;
                if (!int.TryParse(spec.Replace(operators[i], "").Trim(), out limit)) return false;
                int compare = 0.CompareTo(limit);   // == CompareInt(spec, 0)
                switch (operators[i])
                {
                    case "==": return compare == 0;
                    case "!=": return compare != 0;
                    case ">=": return compare >= 0;
                    case "<=": return compare <= 0;
                    case ">": return compare > 0;
                    default: return compare < 0;
                }
            }
            int equality;
            if (int.TryParse(spec, out equality)) return 0 == equality;
            return false;
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
