"""In-add-on UI strings for English / 中文 / 日本語.

A lightweight, self-contained i18n layer driven by the add-on's own ``language``
setting (independent of Blender's UI language). Labels are looked up live in
``draw()`` and via dynamic EnumProperty item callbacks, so switching language
updates the panel immediately.
"""

from __future__ import annotations

LANGUAGES = (
    ("EN", "English", "English"),
    ("ZH", "\u4e2d\u6587", "Chinese"),
    ("JA", "\u65e5\u672c\u8a9e", "Japanese"),
)

# key -> {EN, ZH, JA}
TR = {
    # generic / header
    "language": {"EN": "Language", "ZH": "\u8bed\u8a00", "JA": "\u8a00\u8a9e"},
    "img_size": {"EN": "{w} x {h} px", "ZH": "{w} x {h} \u50cf\u7d20", "JA": "{w} x {h} px"},
    "no_image": {"EN": "No reference image",
                 "ZH": "\u672a\u9009\u62e9\u53c2\u8003\u56fe",
                 "JA": "\u53c2\u7167\u753b\u50cf\u306a\u3057"},

    # mode
    "mode": {"EN": "Mode", "ZH": "\u6a21\u5f0f", "JA": "\u30e2\u30fc\u30c9"},
    "mode_auto": {"EN": "Auto", "ZH": "\u81ea\u52a8", "JA": "\u81ea\u52d5"},
    "mode_auto_desc": {"EN": "Pick portrait or scene automatically from the image",
                       "ZH": "\u6839\u636e\u53c2\u8003\u56fe\u81ea\u52a8\u9009\u62e9\u4eba\u50cf\u6216\u573a\u666f",
                       "JA": "\u753b\u50cf\u304b\u3089\u30dd\u30fc\u30c8\u30ec\u30fc\u30c8/\u30b7\u30fc\u30f3\u3092\u81ea\u52d5\u9078\u629e"},
    "mode_portrait": {"EN": "Portrait / Subject",
                      "ZH": "\u4eba\u50cf / \u4e3b\u4f53",
                      "JA": "\u30dd\u30fc\u30c8\u30ec\u30fc\u30c8 / \u88ab\u5199\u4f53"},
    "mode_portrait_desc": {"EN": "Three-point rig: tight key, soft fill, hard rim on the subject",
                           "ZH": "\u4e09\u70b9\u5e03\u5149\uff1a\u7d27\u51d1\u4e3b\u5149\u3001\u67d4\u548c\u8865\u5149\u3001\u8f6e\u5ed3\u5206\u79bb\u5149",
                           "JA": "\u30bf\u30fc\u30b2\u30c3\u30c8\u7528\u306e\u30ad\u30fc\u30fb\u30d5\u30a3\u30eb\u30fb\u30ea\u30e0\u306e\u4e09\u70b9\u30e9\u30a4\u30c8"},
    "mode_scene": {"EN": "Scene / Product",
                   "ZH": "\u573a\u666f / \u4ea7\u54c1",
                   "JA": "\u30b7\u30fc\u30f3 / \u88fd\u54c1"},
    "mode_scene_desc": {"EN": "Broad even lighting: soft wrap fill + overhead sky (no rim)",
                        "ZH": "\u5e74\u8861\u5e03\u5149\uff1a\u5305\u895f\u8865\u5149 + \u9876\u90e8\u5929\u5149\uff08\u65e0\u8f6e\u5ed3\uff09",
                        "JA": "\u5747\u4e00\u7167\u660e\uff1a\u5305\u307f\u8fbc\u307f\u30d5\u30a3\u30eb\u3068\u5929\u5149\uff08\u30ea\u30e0\u306a\u3057\uff09"},

    # target
    "target": {"EN": "Aim At", "ZH": "\u5bf9\u51c6", "JA": "\u6ce8\u8996\u5148"},
    "target_selected": {"EN": "Active Object",
                        "ZH": "\u6d3b\u52a8\u7269\u4f53",
                        "JA": "\u30a2\u30af\u30c6\u30a3\u30d6\u30aa\u30d6\u30b8\u30a7\u30af\u30c8"},
    "target_selected_desc": {"EN": "Use the active object's geometry bounds (origin-independent)",
                             "ZH": "\u4f7f\u7528\u6d3b\u52a8\u7269\u4f53\u7684\u51e0\u4f55\u5305\u56f4\u76d2(\u4e0e\u539f\u70b9\u65e0\u5173)",
                             "JA": "\u30a2\u30af\u30c6\u30a3\u30d6\u30aa\u30d6\u30b8\u30a7\u30af\u30c8\u306e\u30b8\u30aa\u30e1\u30c8\u30ea\u5883\u754c\u3092\u4f7f\u7528(\u539f\u70b9\u306b\u4f9d\u5b58\u3057\u306a\u3044)"},
    "target_cursor": {"EN": "3D Cursor", "ZH": "3D \u6e38\u6807", "JA": "3D \u30ab\u30fc\u30bd\u30eb"},
    "target_cursor_desc": {"EN": "Use the 3D cursor position",
                           "ZH": "\u4f7f\u7528 3D \u6e38\u6807\u4f4d\u7f6e",
                           "JA": "3D \u30ab\u30fc\u30bd\u30eb\u306e\u4f4d\u7f6e\u3092\u4f7f\u7528"},
    "target_origin": {"EN": "World Origin", "ZH": "\u4e16\u754c\u539f\u70b9", "JA": "\u30ef\u30fc\u30eb\u30c9\u539f\u70b9"},
    "target_origin_desc": {"EN": "Use the world origin",
                           "ZH": "\u4f7f\u7528\u4e16\u754c\u539f\u70b9",
                           "JA": "\u30ef\u30fc\u30eb\u30c9\u539f\u70b9\u3092\u4f7f\u7528"},

    # orient
    "orient": {"EN": "Orient By", "ZH": "\u671d\u5411\u53c2\u7167", "JA": "\u5411\u304d\u306e\u57fa\u6e96"},
    "orient_camera": {"EN": "Active Camera", "ZH": "\u6d3b\u52a8\u76f8\u673a", "JA": "\u30a2\u30af\u30c6\u30a3\u30d6\u30ab\u30e1\u30e9"},
    "orient_camera_desc": {"EN": "Map image axes to the active camera",
                           "ZH": "\u5c06\u56fe\u50cf\u8f74\u6620\u5c04\u5230\u6d3b\u52a8\u76f8\u673a",
                           "JA": "\u753b\u50cf\u8ef8\u3092\u30a2\u30af\u30c6\u30a3\u30d6\u30ab\u30e1\u30e9\u306b\u30de\u30c3\u30d4\u30f3\u30b0"},
    "orient_view": {"EN": "Front (-Y)", "ZH": "\u524d\u89c6\u56fe (-Y)", "JA": "\u6b63\u9762 (-Y)"},
    "orient_view_desc": {"EN": "Map image axes to a front view",
                         "ZH": "\u5c06\u56fe\u50cf\u8f74\u6620\u5c04\u5230\u524d\u89c6\u56fe",
                         "JA": "\u753b\u50cf\u8ef8\u3092\u6b63\u9762\u30d3\u30e5\u30fc\u306b\u30de\u30c3\u30d4\u30f3\u30b0"},

    # buttons
    "generate": {"EN": "Generate Lighting", "ZH": "\u751f\u6210\u706f\u5149", "JA": "\u30e9\u30a4\u30c8\u751f\u6210"},
    "analyze": {"EN": "Analyze Only", "ZH": "\u4ec5\u5206\u6790", "JA": "\u89e3\u6790\u306e\u307f"},
    "clear": {"EN": "Clear", "ZH": "\u6e05\u9664", "JA": "\u30af\u30ea\u30a2"},

    # tuning
    "tuning": {"EN": "Tuning", "ZH": "\u5fae\u8c03", "JA": "\u8abf\u6574"},
    "lock_tuning": {"EN": "Lock — keep this value when switching Strategy",
                    "ZH": "\u9501\u5b9a \u2014 \u5207\u6362\u7b56\u7565\u65f6\u4fdd\u7559\u6b64\u53c2\u6570",
                    "JA": "\u30ed\u30c3\u30af \u2014 \u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u3053\u306e\u5024\u3092\u7dad\u6301"},
    "desc_lock_intensity": {"EN": "Lock intensity when switching Strategy presets",
                            "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u5f3a\u5ea6",
                            "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u5f37\u5ea6\u3092\u30ed\u30c3\u30af"},
    "desc_lock_exposure": {"EN": "Lock exposure scale when switching Strategy presets",
                           "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u66dd\u5149\u7cfb\u6570",
                           "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u9732\u5149\u500d\u7387\u3092\u30ed\u30c3\u30af"},
    "desc_lock_distance": {"EN": "Lock distance when switching Strategy presets",
                           "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u8ddd\u79bb",
                           "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u8ddd\u96e2\u3092\u30ed\u30c3\u30af"},
    "desc_lock_rig_rotation": {"EN": "Lock rig rotation when switching Strategy presets",
                               "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u65cb\u8f6c",
                               "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u56de\u8ee2\u3092\u30ed\u30c3\u30af"},
    "desc_lock_rig_height": {"EN": "Lock rig height when switching Strategy presets",
                            "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u9ad8\u5ea6",
                            "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u9ad8\u3055\u3092\u30ed\u30c3\u30af"},
    "desc_lock_color_strength": {"EN": "Lock color strength when switching Strategy presets",
                                 "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u989c\u8272\u5f3a\u5ea6",
                                 "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u8272\u306e\u5f37\u3055\u3092\u30ed\u30c3\u30af"},
    "desc_lock_color_saturation": {"EN": "Lock saturation when switching Strategy presets",
                                   "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u9971\u548c\u5ea6",
                                   "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u5f69\u5ea6\u3092\u30ed\u30c3\u30af"},
    "desc_lock_tone_shadows": {"EN": "Lock shadow tone when switching Strategy presets",
                               "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u9634\u5f71",
                               "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u30b7\u30e3\u30c9\u30a6\u3092\u30ed\u30c3\u30af"},
    "desc_lock_tone_highlights": {"EN": "Lock highlight tone when switching Strategy presets",
                                  "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u9ad8\u5149",
                                  "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u30cf\u30a4\u30e9\u30a4\u30c8\u3092\u30ed\u30c3\u30af"},
    "desc_lock_contrast_boost": {"EN": "Lock contrast when switching Strategy presets",
                                 "ZH": "\u5207\u6362\u7b56\u7565\u65f6\u9501\u5b9a\u5bf9\u6bd4\u5ea6",
                                 "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc\u5207\u66ff\u6642\u306b\u30b3\u30f3\u30c8\u30e9\u30b9\u30c8\u3092\u30ed\u30c3\u30af"},
    "intensity": {"EN": "Intensity", "ZH": "\u5f3a\u5ea6", "JA": "\u5f37\u5ea6"},
    "exposure": {"EN": "Exposure", "ZH": "\u66dd\u5149\u7cfb\u6570", "JA": "\u9732\u5149\u500d\u7387"},
    "auto_exposure": {"EN": "Auto Exposure", "ZH": "\u81ea\u52a8\u66dd\u5149", "JA": "\u81ea\u52d5\u9732\u5149"},
    "ae_speed": {"EN": "AE Speed", "ZH": "AE \u901f\u5ea6", "JA": "AE \u901f\u5ea6"},
    "ae_center_weight": {"EN": "Center Weight", "ZH": "\u4e2d\u5fc3\u52a0\u6743", "JA": "\u4e2d\u592e\u91cd\u307f"},
    "ae_gamma": {"EN": "Parameter Correction", "ZH": "\u53c2\u6570\u6821\u6b63", "JA": "\u30d1\u30e9\u30e1\u30fc\u30bf\u88dc\u6b63"},
    "ae_cm_exposure": {
        "EN": "CM Exposure: {exp}",
        "ZH": "\u8272\u5f69\u7ba1\u7406\u66dd\u5149\uff1a{exp}",
        "JA": "CM \u66dd\u5149: {exp}",
    },
    "distance": {"EN": "Distance", "ZH": "\u8ddd\u79bb", "JA": "\u8ddd\u96e2"},
    "color_strength": {"EN": "Color Strength", "ZH": "\u989c\u8272\u5f3a\u5ea6", "JA": "\u8272\u306e\u5f37\u3055"},
    "saturation": {"EN": "Saturation", "ZH": "\u9971\u548c\u5ea6", "JA": "\u5f69\u5ea6"},
    "shadows": {"EN": "Shadows", "ZH": "\u9634\u5f71", "JA": "\u30b7\u30e3\u30c9\u30a6"},
    "highlights": {"EN": "Highlights", "ZH": "\u9ad8\u5149", "JA": "\u30cf\u30a4\u30e9\u30a4\u30c8"},
    "contrast": {"EN": "Contrast", "ZH": "\u5bf9\u6bd4\u5ea6", "JA": "\u30b3\u30f3\u30c8\u30e9\u30b9\u30c8"},
    "use_world": {"EN": "Set World / Ambient",
                  "ZH": "\u8bbe\u7f6e\u4e16\u754c / \u73af\u5883\u5149",
                  "JA": "\u30ef\u30fc\u30eb\u30c9 / \u74b0\u5883\u5149\u3092\u8a2d\u5b9a"},
    "backplate": {"EN": "Show Reference as Background",
                  "ZH": "\u663e\u793a\u53c2\u8003\u56fe\u4e3a\u80cc\u666f",
                  "JA": "\u53c2\u7167\u753b\u50cf\u3092\u80cc\u666f\u8868\u793a"},

    # analysis panel
    "detected": {"EN": "Detected Profile", "ZH": "\u68c0\u6d4b\u7ed3\u679c", "JA": "\u691c\u51fa\u30d7\u30ed\u30d5\u30a1\u30a4\u30eb"},
    "colors": {"EN": "Colors", "ZH": "\u989c\u8272", "JA": "\u30ab\u30e9\u30fc"},
    "lbl_mode": {"EN": "Mode", "ZH": "\u6a21\u5f0f", "JA": "\u30e2\u30fc\u30c9"},
    "lbl_mood": {"EN": "Mood", "ZH": "\u5f71\u8c03", "JA": "\u30e0\u30fc\u30c9"},
    "mean_lum": {"EN": "Mean luminance", "ZH": "\u5e73\u5747\u4eae\u5ea6", "JA": "\u5e73\u5747\u8f1d\u5ea6"},
    "lbl_contrast": {"EN": "Contrast (key/fill)",
                     "ZH": "\u5bf9\u6bd4 (\u4e3b/\u8865)",
                     "JA": "\u30b3\u30f3\u30c8\u30e9\u30b9\u30c8 (\u4e3b/\u88dc)"},
    "temp": {"EN": "Temp", "ZH": "\u8272\u6e29", "JA": "\u8272\u6e29\u5ea6"},
    "key_from": {"EN": "Key from", "ZH": "\u4e3b\u5149\u6765\u81ea", "JA": "\u30ad\u30fc\u65b9\u5411"},

    "warm": {"EN": "warm", "ZH": "\u6696", "JA": "\u6696\u8272"},
    "cool": {"EN": "cool", "ZH": "\u51b7", "JA": "\u5bd2\u8272"},
    "neutral": {"EN": "neutral", "ZH": "\u4e2d\u6027", "JA": "\u4e2d\u6027"},

    "mood_high_key": {"EN": "High-key", "ZH": "\u9ad8\u8c03", "JA": "\u30cf\u30a4\u30ad\u30fc"},
    "mood_low_key": {"EN": "Low-key", "ZH": "\u4f4e\u8c03", "JA": "\u30ed\u30fc\u30ad\u30fc"},
    "mood_neutral": {"EN": "Neutral", "ZH": "\u4e2d\u95f4\u8c03", "JA": "\u30cb\u30e5\u30fc\u30c8\u30e9\u30eb"},

    # operator reports
    "err_no_image": {"EN": "No reference image selected",
                     "ZH": "\u672a\u9009\u62e9\u53c2\u8003\u56fe",
                     "JA": "\u53c2\u7167\u753b\u50cf\u304c\u9078\u629e\u3055\u308c\u3066\u3044\u307e\u305b\u3093"},
    "err_analysis": {"EN": "Analysis failed: {err}",
                     "ZH": "\u5206\u6790\u5931\u8d25: {err}",
                     "JA": "\u89e3\u6790\u5931\u6557: {err}"},
    "err_no_file": {"EN": "No valid file selected",
                    "ZH": "\u672a\u9009\u62e9\u6709\u6548\u6587\u4ef6",
                    "JA": "\u6709\u52b9\u306a\u30d5\u30a1\u30a4\u30eb\u304c\u9078\u629e\u3055\u308c\u3066\u3044\u307e\u305b\u3093"},
    "err_load": {"EN": "Could not load image: {err}",
                 "ZH": "\u65e0\u6cd5\u52a0\u8f7d\u56fe\u50cf: {err}",
                 "JA": "\u753b\u50cf\u3092\u8aad\u307f\u8fbc\u3081\u307e\u305b\u3093: {err}"},
    "msg_loaded": {"EN": "Loaded reference: {name}",
                   "ZH": "\u5df2\u8f7d\u5165\u53c2\u8003\u56fe: {name}",
                   "JA": "\u53c2\u7167\u753b\u50cf\u3092\u8aad\u307f\u8fbc\u307f: {name}"},
    "btn_paste": {"EN": "Paste from Clipboard",
                  "ZH": "\u4ece\u526a\u8d34\u677f\u7c98\u8d34",
                  "JA": "\u30af\u30ea\u30c3\u30d7\u30dc\u30fc\u30c9\u304b\u3089\u8cbc\u308a\u4ed8\u3051"},
    "msg_pasted": {"EN": "Pasted reference from clipboard",
                   "ZH": "\u5df2\u4ece\u526a\u8d34\u677f\u7c98\u8d34\u53c2\u8003\u56fe",
                   "JA": "\u30af\u30ea\u30c3\u30d7\u30dc\u30fc\u30c9\u304b\u3089\u53c2\u7167\u3092\u8cbc\u308a\u4ed8\u3051"},
    "err_no_clip": {"EN": "No image found on the clipboard",
                    "ZH": "\u526a\u8d34\u677f\u4e2d\u6ca1\u6709\u56fe\u50cf",
                    "JA": "\u30af\u30ea\u30c3\u30d7\u30dc\u30fc\u30c9\u306b\u753b\u50cf\u304c\u3042\u308a\u307e\u305b\u3093"},
    "msg_analyzed": {"EN": "Analyzed ({mood}, contrast {c})",
                     "ZH": "\u5206\u6790\u5b8c\u6210 ({mood}, \u5bf9\u6bd4 {c})",
                     "JA": "\u89e3\u6790\u5b8c\u4e86 ({mood}, \u30b3\u30f3\u30c8\u30e9\u30b9\u30c8 {c})"},
    "msg_created": {"EN": "Created {n} lights",
                    "ZH": "\u5df2\u751f\u6210 {n} \u76cf\u706f",
                    "JA": "{n} \u500b\u306e\u30e9\u30a4\u30c8\u3092\u751f\u6210"},
    "msg_removed": {"EN": "Removed {n} objects",
                    "ZH": "\u5df2\u79fb\u9664 {n} \u4e2a\u5bf9\u8c61",
                    "JA": "{n} \u500b\u306e\u30aa\u30d6\u30b8\u30a7\u30af\u30c8\u3092\u524a\u9664"},

    # sections
    "section_advanced": {"EN": "Advanced", "ZH": "\u9ad8\u7ea7", "JA": "\u8a73\u7d30"},
    "section_reference": {"EN": "Reference Image", "ZH": "\u53c2\u8003\u56fe", "JA": "\u53c2\u7167\u753b\u50cf"},
    "section_setup": {"EN": "Rig Setup", "ZH": "\u706f\u5149\u67b6\u8bbe\u7f6e", "JA": "\u30ea\u30b0\u8a2d\u5b9a"},
    "section_presets": {"EN": "Presets", "ZH": "\u9884\u8bbe", "JA": "\u30d7\u30ea\u30bb\u30c3\u30c8"},
    "section_actions": {"EN": "Actions", "ZH": "\u64cd\u4f5c", "JA": "\u64cd\u4f5c"},
    "section_energy": {"EN": "Energy & Exposure", "ZH": "\u80fd\u91cf\u4e0e\u66dd\u5149", "JA": "\u5149\u91cf\u30fb\u9732\u5149"},
    "section_rig": {"EN": "Placement", "ZH": "\u4f4d\u7f6e\u4e0e\u65cb\u8f6c", "JA": "\u914d\u7f6e\u30fb\u56de\u8ee2"},
    "section_color": {"EN": "Color & World", "ZH": "\u989c\u8272\u4e0e\u73af\u5883", "JA": "\u8272\u30fb\u74b0\u5883"},
    "preset_section": {"EN": "Strategy", "ZH": "\u7b56\u7565", "JA": "\u30b9\u30c8\u30e9\u30c6\u30b8\u30fc"},
    "ref_section": {"EN": "Lighting Distribution", "ZH": "\u7167\u660e\u5206\u5e03", "JA": "\u7167\u660e\u5206\u5e03"},
    "float_section": {"EN": "Floating Reference", "ZH": "\u53c2\u8003\u56fe\u60ac\u6d6e", "JA": "\u30d5\u30ed\u30fc\u30c6\u30a3\u30f3\u30b0\u53c2\u7167"},
    "glass_section": {"EN": "Glass HUD", "ZH": "\u6bdb\u73bb\u7483\u60ac\u6d6e", "JA": "\u30ac\u30e9\u30b9HUD"},
    "glass_ui_show": {"EN": "Glass UI", "ZH": "\u6bdb\u73bb\u7483\u754c\u9762", "JA": "\u30ac\u30e9\u30b9UI"},
    "glass_ui_active": {
        "EN": "Controls are in the viewport glass panel",
        "ZH": "\u63a7\u5236\u9879\u5728\u89c6\u53e3\u6bdb\u73bb\u7483\u9762\u677f\u4e2d",
        "JA": "操作はビューポートのガラスパネルに表示",
    },
    "glass_blur": {"EN": "Blur", "ZH": "\u6a21\u7cca", "JA": "\u30dc\u30b1"},
    "glass_move": {"EN": "Move", "ZH": "\u62d6\u52a8", "JA": "\u79fb\u52d5"},
    "glass_reset": {"EN": "Reset", "ZH": "\u91cd\u7f6e\u4f4d\u7f6e", "JA": "\u4f4d\u7f6e\u30ea\u30bb\u30c3\u30c8"},
    "glass_ref": {"EN": "Ref", "ZH": "\u53c2\u8003", "JA": "\u53c2\u7167"},
    "glass_no_ref": {"EN": "No reference image", "ZH": "\u672a\u8bbe\u7f6e\u53c2\u8003\u56fe", "JA": "\u53c2\u7167\u753b\u50cf\u306a\u3057"},
    "glass_live_on": {"EN": "Live", "ZH": "\u5b9e\u65f6", "JA": "Live"},
    "glass_live_off": {"EN": "Manual", "ZH": "\u624b\u52a8", "JA": "\u624b\u52d5"},
    "glass_drag_hint": {
        "EN": "Advanced \u2192 Move to reposition",
        "ZH": "\u9ad8\u7ea7 \u2192 \u62d6\u52a8\u53ef\u79fb\u52a8",
        "JA": "\u8a73\u7d30 \u2192 \u79fb\u52d5\u3067\u914d\u7f6e",
    },
    "desc_glass_ui_show": {
        "EN": "Full RollLux UI as a frosted-glass panel over the 3D View",
        "ZH": "\u5c06\u6574\u4e2a RollLux \u754c\u9762\u663e\u793a\u4e3a\u89c6\u53e3\u6bdb\u73bb\u7483\u60ac\u6d6e\u9762\u677f",
        "JA": "RollLux \u5168UI\u3092\u30d3\u30e5\u30fc\u4e0a\u306e\u30ac\u30e9\u30b9\u30d1\u30cd\u30eb\u3067\u8868\u793a",
    },
    "desc_glass_ui_blur": {
        "EN": "How much the viewport behind the panel is blurred",
        "ZH": "\u60ac\u6d6e\u6846\u540e\u65b9\u89c6\u53e3\u7684\u6a21\u7cca\u5f3a\u5ea6",
        "JA": "\u30d1\u30cd\u30eb\u80cc\u5f8c\u306e\u30dc\u30b1\u5f37\u5ea6",
    },
    "float_corner": {"EN": "Corner", "ZH": "\u4f4d\u7f6e", "JA": "\u4f4d\u7f6e"},
    "float_scale": {"EN": "Size", "ZH": "\u5927\u5c0f", "JA": "\u30b5\u30a4\u30ba"},
    "float_opacity": {"EN": "Opacity", "ZH": "\u4e0d\u900f\u660e\u5ea6", "JA": "\u4e0d\u900f\u660e\u5ea6"},
    "corner_tl": {"EN": "Top Left", "ZH": "\u5de6\u4e0a", "JA": "\u5de6\u4e0a"},
    "corner_tr": {"EN": "Top Right", "ZH": "\u53f3\u4e0a", "JA": "\u53f3\u4e0a"},
    "corner_bl": {"EN": "Bottom Left", "ZH": "\u5de6\u4e0b", "JA": "\u5de6\u4e0b"},
    "corner_br": {"EN": "Bottom Right", "ZH": "\u53f3\u4e0b", "JA": "\u53f3\u4e0b"},
    "light_count": {"EN": "Light Count", "ZH": "\u706f\u5149\u6570\u91cf", "JA": "\u30e9\u30a4\u30c8\u6570"},
    "color_strategy": {"EN": "Color Strategy", "ZH": "\u53d6\u8272\u7b56\u7565", "JA": "\u53d6\u8272\u6226\u7565"},
    "color_strategy_default": {"EN": "Default", "ZH": "\u9ed8\u8ba4", "JA": "\u30c7\u30d5\u30a9\u30eb\u30c8"},
    "color_strategy_default_desc": {"EN": "Faithful dominant colors from the reference",
                                    "ZH": "\u4ece\u53c2\u8003\u56fe\u5fe0\u5b9e\u63d0\u53d6\u4e3b\u8272",
                                    "JA": "\u53c2\u7167\u753b\u50cf\u306e\u4e3b\u8272\u3092\u305d\u306e\u307e\u307e"},
    "color_strategy_vivid": {"EN": "Vivid", "ZH": "\u6781\u8272\u5f69", "JA": "\u30d3\u30d3\u30c3\u30c9"},
    "color_strategy_vivid_desc": {"EN": "Boost saturation for punchy, colorful lighting",
                                  "ZH": "\u63d0\u5347\u9971\u548c\u5ea6\uff0c\u706f\u5149\u8272\u5f69\u66f4\u6d53\u70c8",
                                  "JA": "\u5f69\u5ea6\u3092\u5f37\u3081\u3066\u751f\u304d\u306e\u3044\u3044\u8272\u306b"},
    "color_strategy_soft": {"EN": "Soft", "ZH": "\u67d4\u548c", "JA": "\u30bd\u30d5\u30c8"},
    "color_strategy_soft_desc": {"EN": "Lower saturation toward neutral, gentle tones",
                               "ZH": "\u964d\u4f4e\u9971\u548c\u5ea6\uff0c\u504f\u4e2d\u6027\u67d4\u548c",
                               "JA": "\u5f69\u5ea6\u3092\u6291\u3048\u3066\u67d4\u3089\u304b\u306a\u4e2d\u6027\u8272\u306b"},

    # property tooltips (synced to RNA when language changes)
    "desc_language": {"EN": "UI language for this add-on",
                      "ZH": "\u672c\u63d2\u4ef6\u7684\u754c\u9762\u8bed\u8a00",
                      "JA": "\u3053\u306e\u30a2\u30c9\u30aa\u30f3\u306eUI\u8a00\u8a9e"},
    "desc_reference": {"EN": "Lighting reference image to match",
                       "ZH": "\u7528\u4e8e\u5339\u914d\u7684\u706f\u5149\u53c2\u8003\u56fe",
                       "JA": "\u7167\u660e\u3092\u5408\u308f\u305b\u308b\u53c2\u7167\u753b\u50cf"},
    "desc_lighting_preset": {"EN": "Pick a multi-purpose lighting style",
                             "ZH": "\u9009\u62e9\u591a\u7528\u9014\u706f\u5149\u98ce\u683c\uff08\u7b56\u7565\uff09",
                             "JA": "\u591a\u7528\u9014\u306e\u30e9\u30a4\u30c6\u30a3\u30f3\u30b0\u30b9\u30bf\u30a4\u30eb\u3092\u9078\u629e"},
    "desc_reference_preset": {"EN": "Pick a built-in lighting distribution image",
                              "ZH": "\u9009\u62e9\u5185\u7f6e\u7167\u660e\u5206\u5e03\u53c2\u8003\u56fe",
                              "JA": "\u5185\u8535\u306e\u7167\u660e\u5206\u5e03\u53c2\u7167\u3092\u9078\u629e"},
    "desc_luxpro": {"EN": "Detect reference lighting direction (portrait-tuned multi-signal LuxPro)",
                    "ZH": "\u68c0\u6d4b\u53c2\u8003\u56fe\u6253\u5149\u65b9\u5411\uff08\u4eba\u50cf\u4f18\u5316\u7684 LuxPro \u591a\u4fe1\u53f7\u878d\u5408\uff09",
                    "JA": "\u53c2\u7167\u306e\u6253\u5149\u65b9\u5411\u3092\u691c\u51fa\uff08\u30d7\u30fc\u30c8\u5411\u3051 LuxPro \u591a\u4fe1\u53f7\u878d\u5408\uff09"},
    "desc_light_count": {"EN": "How many lights to generate (key is always kept)",
                         "ZH": "\u751f\u6210\u706f\u5149\u6570\u91cf\uff08\u4e3b\u5149\u59cb\u7ec8\u4fdd\u7559\uff09",
                         "JA": "\u751f\u6210\u3059\u308b\u30e9\u30a4\u30c8\u6570\uff08\u30ad\u30fc\u306f\u5e38\u306b\u4fdd\u6301\uff09"},
    "desc_color_strategy": {"EN": "Global color sampling scheme for lights and detection",
                            "ZH": "\u5f71\u54cd\u706f\u5149\u4e0e\u68c0\u6d4b\u7ed3\u679c\u7684\u5168\u5c40\u53d6\u8272\u65b9\u6848",
                            "JA": "\u30e9\u30a4\u30c8\u3068\u691c\u51fa\u8272\u306b\u5f71\u97ff\u3059\u308b\u5168\u5c40\u53d6\u8272"},
    "desc_live": {"EN": "Apply slider changes to the rig in real time",
                  "ZH": "\u5b9e\u65f6\u5c06\u6ed1\u5757\u8c03\u6574\u5e94\u7528\u5230\u706f\u5149\u67b6",
                  "JA": "\u30b9\u30e9\u30a4\u30c0\u30fc\u306e\u5909\u66f4\u3092\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u3067\u9069\u7528"},
    "desc_intensity": {"EN": "Master multiplier on all light energy",
                       "ZH": "\u6240\u6709\u706f\u5149\u80fd\u91cf\u7684\u603b\u4f53\u500d\u6570",
                       "JA": "\u5168\u30e9\u30a4\u30c8\u306e\u5149\u91cf\u306e\u30de\u30b9\u30bf\u30fc\u500d\u7387"},
    "desc_exposure": {"EN": "Integer exposure (1 = neutral, >1 brighter, negative = darker)",
                      "ZH": "\u6574\u6570\u66dd\u5149\uff081 \u4e2d\u6027\uff0c>1 \u66f4\u4eae\uff0c\u8d1f\u6570\u66f4\u6697\uff09",
                      "JA": "\u66dd\u5149\u500d\u7387\uff081 \u304c\u57fa\u6e96\u3001>1 \u3067\u6607\u304c\u308a\u3001\u8ca0 \u3067\u6697\u304f\uff09"},
    "desc_auto_exposure": {
        "EN": "Samples viewport in Rendered shading; adjusts Color Management exposure",
        "ZH": "\u5728\u6e32\u67d3\u7740\u8272\u4e0b\u91c7\u6837\u89c6\u53e3\uff0c\u8c03\u6574\u8272\u5f69\u7ba1\u7406\u66dd\u5149",
        "JA": "\u30ec\u30f3\u30c0\u30fc\u8868\u793a\u3067\u30d3\u30e5\u30fc\u3092\u30b5\u30f3\u30d7\u30eb\u3057\u3001\u66dd\u5149\u3092\u81ea\u52d5\u8abf\u6574",
    },
    "auto_exposure_hint": {
        "EN": "Material Preview or Rendered; adjusts Scene \u2192 Color Management \u2192 Exposure",
        "ZH": "\u652f\u6301\u6750\u8d28\u9884\u89c8/\u6e32\u67d3\uff1b\u8c03\u6574\u300c\u573a\u666f \u2192 \u8272\u5f69\u7ba1\u7406 \u2192 \u66dd\u5149\u300d",
        "JA": "\u30d7\u30ec\u30d3\u30e5\u30fc/\u30ec\u30f3\u30c0\u30fc\u8868\u793a\u3002\u300c\u30b7\u30fc\u30f3 \u2192 \u8272\u8abf\u6574 \u2192 \u66dd\u5149\u300d\u3092\u8abf\u6574",
    },
    "set_rendered": {
        "EN": "Set Rendered Shading",
        "ZH": "\u5207\u6362\u4e3a\u6e32\u67d3\u7740\u8272",
        "JA": "\u30ec\u30f3\u30c0\u30fc\u8868\u793a\u306b\u5207\u66ff",
    },
    "msg_set_rendered": {
        "EN": "3D View switched to Rendered shading",
        "ZH": "3D \u89c6\u53e3\u5df2\u5207\u6362\u4e3a\u6e32\u67d3\u7740\u8272",
        "JA": "3D \u30d3\u30e5\u30fc\u3092\u30ec\u30f3\u30c0\u30fc\u8868\u793a\u306b\u5207\u308a\u66ff\u3048\u307e\u3057\u305f",
    },
    "err_no_view3d": {
        "EN": "Open a 3D Viewport first",
        "ZH": "\u8bf7\u5148\u6253\u5f00 3D \u89c6\u53e3",
        "JA": "3D \u30d3\u30e5\u30fc\u3092\u958b\u3044\u3066\u304f\u3060\u3055\u3044",
    },
    "desc_ae_speed": {
        "EN": "Speed at which exposure reaches the luminance target",
        "ZH": "\u66dd\u5149\u8ddf\u968f\u4eae\u5ea6\u76ee\u6807\u7684\u901f\u5ea6",
        "JA": "\u76ee\u6a19\u8f89\u5ea6\u3078\u306e\u9069\u5fdc\u901f\u5ea6",
    },
    "desc_ae_center_weight": {
        "EN": "Weight the viewport center more when sampling",
        "ZH": "\u91c7\u6837\u65f6\u5bf9\u89c6\u53e3\u4e2d\u5fc3\u52a0\u6743",
        "JA": "\u753b\u9762\u4e2d\u592e\u3092\u91cd\u8996",
    },
    "desc_ae_gamma": {
        "EN": "Color Management gamma (parameter correction) while Auto Exposure is enabled",
        "ZH": "\u5f00\u542f\u81ea\u52a8\u66dd\u5149\u65f6\u7684\u53c2\u6570\u6821\u6b63\uff08\u8272\u5f69\u7ba1\u7406\u4f3d\u9a6c\uff09",
        "JA": "\u81ea\u52d5\u9732\u5149\u6709\u52b9\u6642\u306e\u30d1\u30e9\u30e1\u30fc\u30bf\u88dc\u6b63\uff08\u8272\u8abf\u6574\u30ac\u30f3\u30de\uff09",
    },
    "desc_distance": {"EN": "Light distance from the target (x subject radius)",
                      "ZH": "\u706f\u5149\u4e0e\u76ee\u6807\u7684\u8ddd\u79bb\uff08\u00d7\u7269\u4f53\u534a\u5f84\uff09",
                      "JA": "\u30bf\u30fc\u30b2\u30c3\u30c8\u304b\u3089\u306e\u8ddd\u96e2\uff08\u00d7\u5bfe\u8c61\u534a\u5f84\uff09"},
    "desc_color_strength": {"EN": "How strongly reference colors tint the lights (above 1 boosts chroma)",
                            "ZH": "\u53c2\u8003\u56fe\u989c\u8272\u7740\u8272\u706f\u5149\u7684\u5f3a\u5ea6\uff08\u8d85\u8fc71\u53ef\u52a0\u5f3a\u8272\u5f69\uff09",
                            "JA": "\u53c2\u7167\u8272\u304c\u30e9\u30a4\u30c8\u306b\u4e0e\u3048\u308b\u5f3a\u3055\uff081\u8d85\u3067\u8272\u5f69\u3092\u5f37\u5316\uff09"},
    "desc_color_saturation": {"EN": "Boost or mute color saturation across lights and world",
                              "ZH": "\u63d0\u5347\u6216\u964d\u4f4e\u706f\u5149\u4e0e\u73af\u5883\u5149\u7684\u9971\u548c\u5ea6",
                              "JA": "\u30e9\u30a4\u30c8\u3068\u74b0\u5883\u5149\u306e\u5f69\u5ea6\u3092\u8abf\u6574"},
    "desc_tone_shadows": {"EN": "Lift or deepen fill, ambient, and world (shadow areas)",
                          "ZH": "\u63d0\u5347\u6216\u538b\u6697\u8865\u5149\u3001\u73af\u5883\u5149\u4e0e\u9634\u5f71\u533a\u57df",
                          "JA": "\u30d5\u30a3\u30eb\u30fb\u74b0\u5883\u5149\u3068\u30b7\u30e3\u30c9\u30a6\u3092\u6607\u3055\u308b/\u6df1\u304f\u3059\u308b"},
    "desc_tone_highlights": {"EN": "Brighten or tame key, rim, and accent lights",
                             "ZH": "\u52a0\u4eae\u6216\u538b\u5236\u4e3b\u5149\u3001\u8f6e\u5ed3\u5149\u4e0e\u70b9\u5149",
                             "JA": "\u30ad\u30fc\u30fb\u30ea\u30e0\u30fb\u30a2\u30af\u30bb\u30f3\u30c8\u306e\u9ad8\u5149\u3092\u5f37\u3081\u308b/\u67d4\u3089\u304b\u306b"},
    "desc_contrast": {"EN": "Push or relax the key/fill contrast",
                      "ZH": "\u589e\u5f3a\u6216\u653e\u677e\u4e3b\u5149\u4e0e\u8865\u5149\u7684\u5bf9\u6bd4",
                      "JA": "\u30ad\u30fc/\u30d5\u30a3\u30eb\u306e\u30b3\u30f3\u30c8\u30e9\u30b9\u30c8\u3092\u5f37\u3081\u308b/\u67d4\u3089\u304b\u304f"},
    "desc_rotate": {"EN": "Orbit the whole light rig around the target",
                    "ZH": "\u7ed5\u76ee\u6807\u65cb\u8f6c\u6574\u4e2a\u706f\u5149\u67b6",
                    "JA": "\u30bf\u30fc\u30b2\u30c3\u30c8\u3092\u4e2d\u5fc3\u306b\u30ea\u30b0\u3092\u56de\u8ee2"},
    "desc_height": {"EN": "Slide the whole light rig up or down along Z",
                    "ZH": "\u6cbf Z \u8f74\u4e0a\u4e0b\u79fb\u52a8\u6574\u4e2a\u706f\u5149\u67b6",
                    "JA": "Z\u8ef8\u306b\u6cbf\u3063\u3066\u30ea\u30b0\u3092\u4e0a\u4e0b\u306b\u79fb\u52d5"},
    "desc_use_world": {"EN": "Drive the world background from the reference",
                       "ZH": "\u6839\u636e\u53c2\u8003\u56fe\u8bbe\u7f6e\u4e16\u754c\u73af\u5883\u5149",
                       "JA": "\u53c2\u7167\u753b\u50cf\u304b\u3089\u30ef\u30fc\u30eb\u30c9\u74b0\u5883\u3092\u8a2d\u5b9a"},
    "desc_timer_interval": {"EN": "Seconds between automatic re-generations",
                            "ZH": "\u81ea\u52a8\u91cd\u65b0\u751f\u6210\u7684\u95f4\u9694\u79d2\u6570",
                            "JA": "\u81ea\u52d5\u518d\u751f\u6210\u306e\u9593\u9694\uff08\u79d2\uff09"},
    "desc_float_show": {"EN": "Show the reference floating in the viewport",
                        "ZH": "\u5728\u89c6\u53e3\u4e2d\u60ac\u6d6e\u663e\u793a\u53c2\u8003\u56fe",
                        "JA": "\u30d3\u30e5\u30fc\u30dd\u30fc\u30c8\u306b\u53c2\u7167\u753b\u50cf\u3092\u30d5\u30ed\u30fc\u30c6\u30a3\u30f3\u30b0\u8868\u793a"},
    "desc_float_opacity": {"EN": "Opacity of the floating reference overlay",
                           "ZH": "\u60ac\u6d6e\u53c2\u8003\u56fe\u7684\u4e0d\u900f\u660e\u5ea6",
                           "JA": "\u30d5\u30ed\u30fc\u30c6\u30a3\u30f3\u30b0\u53c2\u7167\u306e\u4e0d\u900f\u660e\u5ea6"},
    "desc_float_scale": {"EN": "Size of the floating reference overlay",
                         "ZH": "\u60ac\u6d6e\u53c2\u8003\u56fe\u7684\u5927\u5c0f",
                         "JA": "\u30d5\u30ed\u30fc\u30c6\u30a3\u30f3\u30b0\u53c2\u7167\u306e\u5927\u304d\u3055"},
    "desc_default_ref": {"EN": "Default: Broad Light (built-in)",
                         "ZH": "\u9ed8\u8ba4\uff1a\u5bbd\u5149\uff08\u5185\u7f6e\u7167\u660e\u5206\u5e03\uff09",
                         "JA": "\u30c7\u30d5\u30a9\u30eb\u30c8\uff1a\u30d6\u30ed\u30fc\u30c9\u30e9\u30a4\u30c8\uff08\u5185\u8535\uff09"},
    "ref_custom": {"EN": "Loaded Image", "ZH": "\u5df2\u8f7d\u5165\u56fe\u50cf", "JA": "\u8aad\u307f\u8fbc\u307f\u753b\u50cf"},
    "ref_custom_desc": {"EN": "Your manually loaded reference (temporary)",
                        "ZH": "\u624b\u52a8\u8f7d\u5165\u7684\u53c2\u8003\u56fe\uff08\u4e34\u65f6\u663e\u793a\uff09",
                        "JA": "\u624b\u52d5\u8aad\u307f\u8fbc\u307f\u306e\u53c2\u7167\uff08\u4e00\u6642\u8868\u793a\uff09"},
    "ref_library_pick": {"EN": "Built-in library",
                         "ZH": "\u5185\u7f6e\u56fe\u5e93",
                         "JA": "\u5185\u8535\u30e9\u30a4\u30d6\u30e9\u30ea"},
    "desc_mode": {"EN": "What kind of lighting rig to build",
                  "ZH": "\u8981\u6784\u5efa\u7684\u706f\u5149\u7c7b\u578b",
                  "JA": "\u69cb\u7bc9\u3059\u308b\u30e9\u30a4\u30c6\u30a3\u30f3\u30b0\u306e\u7a2e\u985e"},
    "desc_target": {"EN": "What the lights orbit and aim at",
                    "ZH": "\u706f\u5149\u73af\u7ed5\u5e76\u5bf9\u51c6\u7684\u76ee\u6807",
                    "JA": "\u30e9\u30a4\u30c8\u304c\u56f2\u3080\u30bf\u30fc\u30b2\u30c3\u30c8"},
    "desc_orient": {"EN": "How image axes map into the scene",
                    "ZH": "\u56fe\u50cf\u8f74\u5411\u5982\u4f55\u6620\u5c04\u5230\u573a\u666f",
                    "JA": "\u753b\u50cf\u8ef8\u3092\u30b7\u30fc\u30f3\u306b\u30de\u30c3\u30d4\u30f3\u30b0\u3059\u308b\u57fa\u6e96"},

    # lighting presets
    "preset_random": {"EN": "Random", "ZH": "\u968f\u673a", "JA": "\u30e9\u30f3\u30c0\u30e0"},
    "preset_random_desc": {"EN": "Randomly generated lighting style",
                           "ZH": "\u968f\u673a\u751f\u6210\u7684\u706f\u5149\u98ce\u683c",
                           "JA": "\u30e9\u30f3\u30c0\u30e0\u751f\u6210\u306e\u30e9\u30a4\u30c6\u30a3\u30f3\u30b0"},
    "preset_auto": {"EN": "Auto", "ZH": "\u81ea\u52a8", "JA": "\u81ea\u52d5"},
    "preset_auto_desc": {"EN": "Use the analyzed profile as-is",
                         "ZH": "\u76f4\u63a5\u4f7f\u7528\u5206\u6790\u7ed3\u679c",
                         "JA": "\u89e3\u6790\u7d50\u679c\u3092\u305d\u306e\u307e\u307e\u4f7f\u7528"},
    "preset_portrait": {"EN": "Portrait", "ZH": "\u4eba\u50cf", "JA": "\u30dd\u30fc\u30c8\u30ec\u30fc\u30c8"},
    "preset_portrait_desc": {"EN": "Balanced three-point portrait rig",
                             "ZH": "\u5747\u8861\u7684\u4e09\u70b9\u4eba\u50cf\u5e03\u5149",
                             "JA": "\u30d0\u30e9\u30f3\u30b9\u306e\u53d6\u308c\u305f\u4e09\u70b9\u30e9\u30a4\u30c8"},
    "preset_cinematic": {"EN": "Cinematic", "ZH": "\u7535\u5f71\u611f", "JA": "\u30b7\u30cd\u30de\u30c6\u30a3\u30c3\u30af"},
    "preset_cinematic_desc": {"EN": "High-contrast, strong rim, narrow key",
                              "ZH": "\u9ad8\u5bf9\u6bd4\u3001\u5f3a\u8f6e\u5ed3\u5149\u3001\u7a84\u4e3b\u5149",
                              "JA": "\u9ad8\u30b3\u30f3\u30c8\u30e9\u30b9\u30c8\u30fb\u5f37\u3044\u30ea\u30e0"},
    "preset_studio": {"EN": "Studio", "ZH": "\u5f71\u68da", "JA": "\u30b9\u30bf\u30b8\u30aa"},
    "preset_studio_desc": {"EN": "Soft, even, neutral product lighting",
                           "ZH": "\u67d4\u548c\u5747\u5300\u7684\u4e2d\u6027\u4ea7\u54c1\u5149",
                           "JA": "\u67d4\u3089\u304b\u304f\u5747\u4e00\u306a\u88fd\u54c1\u7167\u660e"},
    "preset_dramatic": {"EN": "Dramatic", "ZH": "\u620f\u5267\u5149", "JA": "\u30c9\u30e9\u30de\u30c1\u30c3\u30af"},
    "preset_dramatic_desc": {"EN": "Single hard key, deep shadows",
                             "ZH": "\u5355\u4e3b\u786c\u5149\u3001\u6df1\u9634\u5f71",
                             "JA": "\u5358\u4e00\u306e\u30cf\u30fc\u30c9\u30ad\u30fc\u30fb\u6df1\u3044\u5f71"},
    "preset_beauty": {"EN": "Beauty", "ZH": "\u7f8e\u5986\u67d4\u5149", "JA": "\u30d3\u30e5\u30fc\u30c6\u30a3"},
    "preset_beauty_desc": {"EN": "Large soft frontal, low contrast",
                           "ZH": "\u5927\u9762\u79ef\u6b63\u9762\u67d4\u5149\u3001\u4f4e\u5bf9\u6bd4",
                           "JA": "\u5927\u304d\u306a\u6b63\u9762\u30bd\u30d5\u30c8\u30fb\u4f4e\u30b3\u30f3\u30c8\u30e9\u30b9\u30c8"},
    "preset_outdoor": {"EN": "Outdoor", "ZH": "\u6237\u5916", "JA": "\u30a2\u30a6\u30c8\u30c9\u30a2"},
    "preset_outdoor_desc": {"EN": "Sun key + cool sky fill",
                            "ZH": "\u9633\u5149\u4e3b\u5149 + \u51b7\u8c03\u5929\u7a7a\u8865\u5149",
                            "JA": "\u592a\u967d\u30ad\u30fc + \u5bd2\u8272\u306e\u7a7a\u88dc\u5149"},
    "preset_rembrandt": {"EN": "Rembrandt", "ZH": "\u4f26\u52c3\u6717\u5149", "JA": "\u30ec\u30f3\u30d6\u30e9\u30f3\u30c8"},
    "preset_rembrandt_desc": {"EN": "45\u00b0 key, triangle cheek light",
                              "ZH": "45\u00b0\u4e3b\u5149\uff0c\u9830\u90e8\u4e09\u89d2\u5149",
                              "JA": "45\u5ea6\u30ad\u30fc\u3001\u982c\u306e\u4e09\u89d2\u5149"},
    "preset_butterfly": {"EN": "Butterfly", "ZH": "\u8774\u8776\u5149", "JA": "\u30d0\u30bf\u30d5\u30e9\u30a4"},
    "preset_butterfly_desc": {"EN": "Frontal high key, nose shadow",
                              "ZH": "\u6b63\u9762\u9ad8\u4f4d\u4e3b\u5149\uff0c\u9f3b\u4e0b\u8776\u5f71",
                              "JA": "\u6b63\u9762\u30cf\u30a4\u30ad\u30fc\u3001\u9f3b\u4e0b\u306e\u5f71"},
    "preset_loop": {"EN": "Loop", "ZH": "\u73af\u5f62\u5149", "JA": "\u30eb\u30fc\u30d7"},
    "preset_loop_desc": {"EN": "Slight side key, small nose loop",
                         "ZH": "\u7565\u504f\u4fa7\u4e3b\u5149\uff0c\u9f3b\u4fa7\u73af\u5f71",
                         "JA": "\u3084\u3084\u6a2a\u304b\u3089\u306e\u30ad\u30fc"},
    "preset_split": {"EN": "Split", "ZH": "\u5206\u5272\u5149", "JA": "\u30b9\u30d7\u30ea\u30c3\u30c8"},
    "preset_split_desc": {"EN": "Hard 90\u00b0 side, half-lit face",
                          "ZH": "90\u00b0\u786c\u4fa7\u5149\uff0c\u534a\u8fb9\u8138",
                          "JA": "\u771f\u6a2a\u304b\u3089\u306e\u5206\u5272\u5149"},
    "preset_clamshell": {"EN": "Clamshell", "ZH": "\u868c\u58f3\u5149", "JA": "\u30af\u30e9\u30e0\u30b7\u30a7\u30eb"},
    "preset_clamshell_desc": {"EN": "Top + bottom soft beauty",
                              "ZH": "\u4e0a\u4e0b\u53cc\u67d4\u5149\u7f8e\u989c",
                              "JA": "\u4e0a\u4e0b\u306e\u30bd\u30d5\u30c8\u7f8e\u5149"},
    "preset_noir": {"EN": "Film Noir", "ZH": "\u9ed1\u8272\u7535\u5f71", "JA": "\u30d5\u30a3\u30eb\u30e0\u30ce\u30ef\u30fc\u30eb"},
    "preset_noir_desc": {"EN": "Hard single key, crushed shadows",
                         "ZH": "\u5355\u786c\u4e3b\u5149\uff0c\u6781\u6df1\u9634\u5f71",
                         "JA": "\u30cf\u30fc\u30c9\u306a\u5358\u4e00\u5149\u3001\u6df1\u3044\u5f71"},
    "preset_low_key": {"EN": "Low Key", "ZH": "\u4f4e\u8c03\u5149", "JA": "\u30ed\u30fc\u30ad\u30fc"},
    "preset_low_key_desc": {"EN": "Dark, moody, minimal fill",
                            "ZH": "\u6697\u8c03\u60c5\u7eea\uff0c\u6781\u5c11\u8865\u5149",
                            "JA": "\u6697\u304f\u30e0\u30fc\u30c7\u30a3\u3001\u88dc\u52a9\u5149\u63a7\u3048\u3081"},
    "preset_high_key": {"EN": "High Key", "ZH": "\u9ad8\u8c03\u5149", "JA": "\u30cf\u30a4\u30ad\u30fc"},
    "preset_high_key_desc": {"EN": "Bright, airy, shadowless",
                             "ZH": "\u660e\u4eae\u901a\u900f\uff0c\u51e0\u4e4e\u65e0\u5f71",
                             "JA": "\u660e\u308b\u304f\u5f71\u306e\u5c11\u306a\u3044"},
    "preset_product": {"EN": "Product", "ZH": "\u4ea7\u54c1\u5149", "JA": "\u30d7\u30ed\u30c0\u30af\u30c8"},
    "preset_product_desc": {"EN": "Clean even with edge accent",
                            "ZH": "\u5e72\u51c0\u5747\u5300\uff0c\u8fb9\u7f18\u5f3a\u8c03",
                            "JA": "\u5747\u4e00\u3067\u30a8\u30c3\u30b8\u5f37\u8abf"},
    "preset_soft_even": {"EN": "Soft Even", "ZH": "\u67d4\u548c\u5747\u5149", "JA": "\u30bd\u30d5\u30c8\u5747\u4e00"},
    "preset_soft_even_desc": {"EN": "Flat wraparound soft light",
                              "ZH": "\u5e73\u6574\u5305\u88f9\u5f0f\u67d4\u5149",
                              "JA": "\u5e73\u5766\u3067\u5305\u307f\u8fbc\u3080\u67d4\u5149"},
    "preset_rim": {"EN": "Rim / Hair", "ZH": "\u8f6e\u5ed3\u5149", "JA": "\u30ea\u30e0/\u30d8\u30a2"},
    "preset_rim_desc": {"EN": "Strong separating edge light",
                        "ZH": "\u5f3a\u5206\u79bb\u8fb9\u7f18\u5149",
                        "JA": "\u5f37\u3044\u5206\u96e2\u30a8\u30c3\u30b8\u5149"},
    "preset_backlight": {"EN": "Backlight", "ZH": "\u9006\u5149", "JA": "\u30d0\u30c3\u30af\u30e9\u30a4\u30c8"},
    "preset_backlight_desc": {"EN": "Bright behind, glowing edges",
                              "ZH": "\u80cc\u540e\u5f3a\u5149\uff0c\u53d1\u5149\u8fb9\u7f18",
                              "JA": "\u80cc\u5f8c\u304b\u3089\u3001\u7e01\u304c\u5149\u308b"},
    "preset_sunset": {"EN": "Sunset", "ZH": "\u65e5\u843d", "JA": "\u30b5\u30f3\u30bb\u30c3\u30c8"},
    "preset_sunset_desc": {"EN": "Warm low sun, long shadows",
                           "ZH": "\u6696\u8272\u4f4e\u4f4d\u9633\u5149\uff0c\u957f\u5f71",
                           "JA": "\u6696\u8272\u306e\u4f4e\u3044\u592a\u967d\u3001\u9577\u3044\u5f71"},
    "preset_twilight": {"EN": "Twilight", "ZH": "\u66ae\u8272", "JA": "\u30c8\u30ef\u30a4\u30e9\u30a4\u30c8"},
    "preset_twilight_desc": {"EN": "Cool soft ambient dusk",
                             "ZH": "\u51b7\u8c03\u67d4\u548c\u9ec4\u660f\u73af\u5149",
                             "JA": "\u5bd2\u8272\u306e\u67d4\u3089\u304b\u306a\u5915\u66ae"},
    "preset_neon": {"EN": "Neon", "ZH": "\u9713\u8679", "JA": "\u30cd\u30aa\u30f3"},
    "preset_neon_desc": {"EN": "Magenta key, cyan rim",
                         "ZH": "\u54c1\u7ea2\u4e3b\u5149\uff0c\u9752\u8272\u8f6e\u5ed3",
                         "JA": "\u30de\u30bc\u30f3\u30bf\u30ad\u30fc\u3001\u30b7\u30a2\u30f3\u30ea\u30e0"},
    "preset_candlelight": {"EN": "Candlelight", "ZH": "\u70db\u5149", "JA": "\u30ad\u30e3\u30f3\u30c9\u30eb"},
    "preset_candlelight_desc": {"EN": "Warm flickering point light",
                                "ZH": "\u6696\u8272\u6447\u66f3\u70b9\u5149",
                                "JA": "\u6696\u8272\u306e\u70b9\u5149\u6e90"},
    "preset_moonlight": {"EN": "Moonlight", "ZH": "\u6708\u5149", "JA": "\u30e0\u30fc\u30f3\u30e9\u30a4\u30c8"},
    "preset_moonlight_desc": {"EN": "Cool dim directional night",
                              "ZH": "\u51b7\u8c03\u5fae\u5f31\u65b9\u5411\u591c\u5149",
                              "JA": "\u5bd2\u8272\u3067\u6de1\u3044\u65b9\u5411\u5149"},
    "preset_underlight": {"EN": "Underlight", "ZH": "\u5e95\u5149", "JA": "\u30a2\u30f3\u30c0\u30fc\u30e9\u30a4\u30c8"},
    "preset_underlight_desc": {"EN": "Eerie light from below",
                               "ZH": "\u8be1\u5f02\u7684\u5e95\u90e8\u6253\u5149",
                               "JA": "\u4e0d\u6c17\u5473\u306a\u4e0b\u304b\u3089\u306e\u5149"},

    # reference library names/descriptions are injected from _REF_I18N below.

    # LuxPro / tuning
    "luxpro": {"EN": "LuxPro Direction", "ZH": "LuxPro \u65b9\u5411", "JA": "LuxPro \u65b9\u5411"},
    "rotate": {"EN": "Rotate Rig", "ZH": "\u65cb\u8f6c\u706f\u5149", "JA": "\u30ea\u30b0\u56de\u8ee2"},
    "height": {"EN": "Light Height", "ZH": "\u706f\u5149\u9ad8\u5ea6", "JA": "\u30e9\u30a4\u30c8\u9ad8\u3055"},
    "err_no_rig": {"EN": "Generate a light rig first",
                   "ZH": "\u8bf7\u5148\u751f\u6210\u706f\u5149",
                   "JA": "\u5148\u306b\u30e9\u30a4\u30c8\u3092\u751f\u6210\u3057\u3066\u304f\u3060\u3055\u3044"},
    "timer_generate": {"EN": "Auto Generate", "ZH": "\u5b9a\u65f6\u751f\u6210", "JA": "\u81ea\u52d5\u751f\u6210"},
    "timer_interval": {"EN": "Interval", "ZH": "\u95f4\u9694", "JA": "\u9593\u9694"},
    "msg_timer_on": {"EN": "Auto-generate timer started",
                     "ZH": "\u5b9a\u65f6\u751f\u6210\u5df2\u5f00\u542f",
                     "JA": "\u81ea\u52d5\u751f\u6210\u30bf\u30a4\u30de\u30fc\u3092\u958b\u59cb"},
    "msg_timer_off": {"EN": "Auto-generate timer stopped",
                      "ZH": "\u5b9a\u65f6\u751f\u6210\u5df2\u505c\u6b62",
                      "JA": "\u81ea\u52d5\u751f\u6210\u30bf\u30a4\u30de\u30fc\u3092\u505c\u6b62"},

    # lights panel
    "lights_section": {"EN": "Lights", "ZH": "\u706f\u5149", "JA": "\u30e9\u30a4\u30c8"},
    "light_energy": {"EN": "Energy", "ZH": "\u5f3a\u5ea6", "JA": "\u5f37\u5ea6"},
    "light_softness": {"EN": "Soft", "ZH": "\u67d4\u5316", "JA": "\u67d4\u3089\u304b\u3055"},
    "role_key": {"EN": "Key", "ZH": "\u4e3b\u5149", "JA": "\u30ad\u30fc"},
    "role_fill": {"EN": "Fill", "ZH": "\u8865\u5149", "JA": "\u30d5\u30a3\u30eb"},
    "role_rim": {"EN": "Rim", "ZH": "\u8f6e\u5ed3\u5149", "JA": "\u30ea\u30e0"},
    "role_sky": {"EN": "Sky", "ZH": "\u5929\u5149", "JA": "\u5929\u5149"},
    "role_accent": {"EN": "Accent", "ZH": "\u4fee\u9970\u5149", "JA": "\u30a2\u30af\u30bb\u30f3\u30c8"},
    "role_extra": {"EN": "Extra", "ZH": "\u989d\u5916\u706f", "JA": "\u8ffd\u52a0\u30e9\u30a4\u30c8"},

    # direction labels
    "dir_left": {"EN": "Left", "ZH": "\u5de6\u4fa7", "JA": "\u5de6"},
    "dir_right": {"EN": "Right", "ZH": "\u53f3\u4fa7", "JA": "\u53f3"},
    "dir_top": {"EN": "Top", "ZH": "\u9876\u5149", "JA": "\u4e0a"},
    "dir_bottom": {"EN": "Bottom", "ZH": "\u5e95\u5149", "JA": "\u4e0b"},
    "dir_center": {"EN": "Center", "ZH": "\u4e2d\u5fc3", "JA": "\u4e2d\u592e"},
    "dir_front": {"EN": "Front / Flat", "ZH": "\u6b63\u9762/\u5e73\u5149", "JA": "\u6b63\u9762/\u30d5\u30e9\u30c3\u30c8"},
    "dir_top_left": {"EN": "Top-Left", "ZH": "\u5de6\u4e0a\u65b9", "JA": "\u5de6\u4e0a"},
    "dir_top_right": {"EN": "Top-Right", "ZH": "\u53f3\u4e0a\u65b9", "JA": "\u53f3\u4e0a"},
    "dir_bottom_left": {"EN": "Bottom-Left", "ZH": "\u5de6\u4e0b\u65b9", "JA": "\u5de6\u4e0b"},
    "dir_bottom_right": {"EN": "Bottom-Right", "ZH": "\u53f3\u4e0b\u65b9", "JA": "\u53f3\u4e0b"},
    "dir_backlight": {"EN": "Backlight / Rim", "ZH": "\u80cc\u5149/\u8f6e\u5ed3", "JA": "\u9006\u5149/\u30ea\u30e0"},

    # operator reports
    "msg_light_deleted": {"EN": "Light deleted", "ZH": "\u5df2\u5220\u9664\u706f\u5149", "JA": "\u30e9\u30a4\u30c8\u3092\u524a\u9664"},
    "random_generate": {"EN": "Random", "ZH": "\u968f\u673a\u751f\u6210", "JA": "\u30e9\u30f3\u30c0\u30e0\u751f\u6210"},
    "msg_random_preset": {"EN": "Generated a random lighting preset",
                          "ZH": "\u5df2\u968f\u673a\u751f\u6210\u706f\u5149\u9884\u8bbe",
                          "JA": "\u30e9\u30f3\u30c0\u30e0\u306a\u30e9\u30a4\u30c8\u30d7\u30ea\u30bb\u30c3\u30c8\u3092\u751f\u6210"},
    "msg_random_reference": {"EN": "Generated a random reference image",
                             "ZH": "\u5df2\u968f\u673a\u751f\u6210\u53c2\u8003\u56fe",
                             "JA": "\u30e9\u30f3\u30c0\u30e0\u306a\u53c2\u7167\u753b\u50cf\u3092\u751f\u6210"},
}


# Reference library: (EN name, ZH name, JA name, EN desc, ZH desc, JA desc).
# Kept compact and merged into TR as ref_<id> / ref_<id>_desc below.
_REF_I18N = {
    "random": ("Random", "\u968f\u673a", "\u30e9\u30f3\u30c0\u30e0",
               "Randomly generated lighting distribution",
               "\u968f\u673a\u751f\u6210\u7684\u7167\u660e\u5206\u5e03",
               "\u30e9\u30f3\u30c0\u30e0\u751f\u6210\u306e\u7167\u660e\u5206\u5e03"),
    "golden_hour": ("Golden Hour", "\u9ec4\u91d1\u65f6\u523b", "\u30b4\u30fc\u30eb\u30c7\u30f3\u30a2\u30ef\u30fc",
                    "Warm key from the right", "\u53f3\u4fa7\u6696\u5149", "\u53f3\u304b\u3089\u306e\u6696\u8272\u5149"),
    "sunrise": ("Sunrise", "\u65e5\u51fa", "\u65e5\u306e\u51fa",
                "Soft warm light from the left", "\u5de6\u4fa7\u67d4\u548c\u6696\u5149", "\u5de6\u304b\u3089\u306e\u67d4\u3089\u304b\u3044\u6696\u5149"),
    "sunset": ("Sunset", "\u65e5\u843d", "\u30b5\u30f3\u30bb\u30c3\u30c8",
               "Deep orange low sun", "\u6a59\u7ea2\u8272\u4f4e\u4f4d\u9633\u5149", "\u6df1\u3044\u30aa\u30ec\u30f3\u30b8\u306e\u592a\u967d"),
    "blue_hour": ("Blue Hour", "\u84dd\u8c03\u65f6\u523b", "\u30d6\u30eb\u30fc\u30a2\u30ef\u30fc",
                  "Cool dim top light", "\u51b7\u8c03\u6697\u90e8\u9876\u5149", "\u5bd2\u8272\u306e\u6697\u3044\u30c8\u30c3\u30d7\u5149"),
    "twilight": ("Twilight", "\u66ae\u8272", "\u30c8\u30ef\u30a4\u30e9\u30a4\u30c8",
                 "Cool sky with magenta glow", "\u51b7\u8c03\u5929\u7a7a\u5e26\u54c1\u7ea2\u8f89", "\u5bd2\u8272\u306e\u7a7a\u3068\u30de\u30bc\u30f3\u30bf"),
    "midday": ("Midday", "\u6b63\u5348", "\u771f\u663c",
               "Bright neutral overhead", "\u660e\u4eae\u4e2d\u6027\u9876\u5149", "\u660e\u308b\u3044\u4e2d\u6027\u306e\u4e0a\u5149"),
    "harsh_noon": ("Harsh Noon", "\u6b63\u5348\u786c\u5149", "\u771f\u663c\u306e\u5f37\u5149",
                   "Hard overhead sun", "\u5934\u9876\u786c\u9633\u5149", "\u982d\u4e0a\u306e\u5f37\u3044\u592a\u967d"),
    "overcast": ("Overcast", "\u9634\u5929", "\u66c7\u5929",
                 "Flat soft daylight", "\u5e73\u5300\u67d4\u548c\u65e5\u5149", "\u5e73\u5766\u306a\u67d4\u3089\u304b\u3044\u663c\u5149"),
    "foggy_morn": ("Foggy Morning", "\u96fe\u6668", "\u9727\u306e\u671d",
                   "Low contrast misty light", "\u4f4e\u5bf9\u6bd4\u8ff7\u96fe\u5149", "\u4f4e\u30b3\u30f3\u30c8\u30e9\u30b9\u30c8\u306e\u9727"),
    "night_sky": ("Night Sky", "\u591c\u7a7a", "\u591c\u7a7a",
                  "Dark with a cool highlight", "\u6697\u8c03\u51b7\u8c03\u9ad8\u5149", "\u6697\u304f\u5bd2\u8272\u306e\u30cf\u30a4\u30e9\u30a4\u30c8"),
    "top_sky": ("Top Sky", "\u9876\u5149\u5929\u7a7a", "\u30c8\u30c3\u30d7\u30b9\u30ab\u30a4",
                "Bright sky from above", "\u4e0a\u65b9\u660e\u4eae\u5929\u5149", "\u4e0a\u65b9\u304b\u3089\u306e\u660e\u308b\u3044\u7a7a\u5149"),
    "softbox": ("Softbox", "\u67d4\u5149\u7bb1", "\u30bd\u30d5\u30c8\u30dc\u30c3\u30af\u30b9",
                "Bright even soft light", "\u660e\u4eae\u5747\u5300\u67d4\u5149", "\u660e\u308b\u304f\u5747\u4e00\u306a\u67d4\u5149"),
    "softbox_l": ("Softbox Left", "\u5de6\u4fa7\u67d4\u5149", "\u30bd\u30d5\u30c8\u30dc\u30c3\u30af\u30b9\u5de6",
                  "Soft key from the left", "\u5de6\u4fa7\u67d4\u4e3b\u5149", "\u5de6\u304b\u3089\u306e\u30bd\u30d5\u30c8\u30ad\u30fc"),
    "softbox_r": ("Softbox Right", "\u53f3\u4fa7\u67d4\u5149", "\u30bd\u30d5\u30c8\u30dc\u30c3\u30af\u30b9\u53f3",
                  "Soft key from the right", "\u53f3\u4fa7\u67d4\u4e3b\u5149", "\u53f3\u304b\u3089\u306e\u30bd\u30d5\u30c8\u30ad\u30fc"),
    "beauty_dish": ("Beauty Dish", "\u96f7\u8fbe\u7f69", "\u30d3\u30e5\u30fc\u30c6\u30a3\u30c7\u30a3\u30c3\u30b7\u30e5",
                    "Crisp frontal beauty light", "\u6e05\u6670\u6b63\u9762\u7f8e\u5149", "\u6b63\u9762\u306e\u30b7\u30e3\u30fc\u30d7\u306a\u7f8e\u5149"),
    "ring_light": ("Ring Light", "\u73af\u5f62\u5149", "\u30ea\u30f3\u30b0\u30e9\u30a4\u30c8",
                   "Centered ring catchlight", "\u4e2d\u5fc3\u73af\u5f62\u5149", "\u4e2d\u592e\u306e\u30ea\u30f3\u30b0\u5149"),
    "clamshell": ("Clamshell", "\u868c\u58f3\u5149", "\u30af\u30e9\u30e0\u30b7\u30a7\u30eb",
                  "Top + bottom soft beauty", "\u4e0a\u4e0b\u53cc\u67d4\u5149", "\u4e0a\u4e0b\u306e\u30bd\u30d5\u30c8\u5149"),
    "butterfly": ("Butterfly", "\u8774\u8776\u5149", "\u30d0\u30bf\u30d5\u30e9\u30a4",
                  "Frontal high beauty key", "\u6b63\u9762\u9ad8\u4f4d\u7f8e\u5149", "\u6b63\u9762\u30cf\u30a4\u306e\u7f8e\u5149"),
    "broad_light": ("Broad Light", "\u5bbd\u5149", "\u30d6\u30ed\u30fc\u30c9\u30e9\u30a4\u30c8",
                    "Lit side toward camera", "\u671d\u955c\u5934\u4e00\u4fa7\u53d7\u5149", "\u30ab\u30e1\u30e9\u5074\u3092\u7167\u3089\u3059"),
    "short_light": ("Short Light", "\u7a84\u5149", "\u30b7\u30e7\u30fc\u30c8\u30e9\u30a4\u30c8",
                    "Lit side away from camera", "\u80cc\u955c\u5934\u4e00\u4fa7\u53d7\u5149", "\u30ab\u30e1\u30e9\u3068\u53cd\u5bfe\u5074\u3092\u7167\u3089\u3059"),
    "high_key": ("High Key", "\u9ad8\u8c03", "\u30cf\u30a4\u30ad\u30fc",
                 "Bright airy near-shadowless", "\u660e\u4eae\u901a\u900f\u51e0\u65e0\u5f71", "\u660e\u308b\u304f\u5f71\u306e\u5c11\u306a\u3044"),
    "low_key": ("Low Key", "\u4f4e\u8c03", "\u30ed\u30fc\u30ad\u30fc",
                "Dark with a single key", "\u6697\u8c03\u5355\u4e3b\u5149", "\u6697\u304f\u5358\u4e00\u306e\u30ad\u30fc"),
    "rembrandt": ("Rembrandt", "\u4f26\u52c3\u6717\u5149", "\u30ec\u30f3\u30d6\u30e9\u30f3\u30c8",
                  "Warm key upper-left, dark", "\u5de6\u4e0a\u6696\u5149\u3001\u6697\u8c03", "\u5de6\u4e0a\u306e\u6696\u8272\u30ad\u30fc"),
    "rembrandt_r": ("Rembrandt Right", "\u53f3\u4f26\u52c3\u6717", "\u30ec\u30f3\u30d6\u30e9\u30f3\u30c8\u53f3",
                    "Warm key upper-right", "\u53f3\u4e0a\u6696\u5149", "\u53f3\u4e0a\u306e\u6696\u8272\u30ad\u30fc"),
    "loop": ("Loop", "\u73af\u5f62\u5149", "\u30eb\u30fc\u30d7",
             "Slight off-center key", "\u7565\u504f\u4e2d\u4e3b\u5149", "\u3084\u3084\u4e2d\u5fc3\u304b\u3089\u305a\u308c\u305f\u30ad\u30fc"),
    "split": ("Split", "\u5206\u5272\u5149", "\u30b9\u30d7\u30ea\u30c3\u30c8",
              "Hard 90\u00b0 side light", "90\u00b0\u786c\u4fa7\u5149", "\u771f\u6a2a\u304b\u3089\u306e\u786c\u3044\u5149"),
    "under_light": ("Under Light", "\u5e95\u5149", "\u30a2\u30f3\u30c0\u30fc\u30e9\u30a4\u30c8",
                    "Eerie light from below", "\u8be1\u5f02\u5e95\u90e8\u6253\u5149", "\u4e0b\u304b\u3089\u306e\u4e0d\u6c17\u5473\u306a\u5149"),
    "hair_light": ("Hair Light", "\u53d1\u5149", "\u30d8\u30a2\u30e9\u30a4\u30c8",
                   "Top rim separation light", "\u9876\u90e8\u8f6e\u5ed3\u5206\u79bb\u5149", "\u4e0a\u90e8\u306e\u30ea\u30e0\u5206\u96e2\u5149"),
    "noir": ("Film Noir", "\u9ed1\u8272\u7535\u5f71", "\u30d5\u30a3\u30eb\u30e0\u30ce\u30ef\u30fc\u30eb",
             "Hard key through blinds", "\u767e\u53f6\u7a97\u786c\u5149", "\u30d6\u30e9\u30a4\u30f3\u30c9\u8d8a\u3057\u306e\u786c\u5149"),
    "teal_orange": ("Teal & Orange", "\u9752\u6a59\u8c03", "\u30c6\u30a3\u30fc\u30eb\uff06\u30aa\u30ec\u30f3\u30b8",
                    "Warm key, teal fill", "\u6696\u4e3b\u5149\u9752\u8865\u5149", "\u6696\u8272\u30ad\u30fc\u3068\u9752\u88dc\u5149"),
    "neon_mc": ("Neon M/C", "\u9713\u8679\u54c1\u9752", "\u30cd\u30aa\u30f3 M/C",
                "Magenta + cyan neon", "\u54c1\u7ea2\u4e0e\u9752\u8272\u9713\u8679", "\u30de\u30bc\u30f3\u30bf\u3068\u30b7\u30a2\u30f3"),
    "neon_bp": ("Neon B/P", "\u9713\u8679\u84dd\u7c89", "\u30cd\u30aa\u30f3 B/P",
                "Blue + pink neon", "\u84dd\u8272\u4e0e\u7c89\u8272\u9713\u8679", "\u9752\u3068\u30d4\u30f3\u30af"),
    "candlelight": ("Candlelight", "\u70db\u5149", "\u30ad\u30e3\u30f3\u30c9\u30eb",
                    "Warm flickering point", "\u6696\u8272\u6447\u66f3\u70b9\u5149", "\u6696\u8272\u306e\u63fa\u3089\u3081\u304f\u70b9\u5149"),
    "firelight": ("Firelight", "\u706b\u5149", "\u706b\u306e\u5149",
                  "Warm glow from below", "\u6765\u81ea\u4e0b\u65b9\u6696\u8f89", "\u4e0b\u304b\u3089\u306e\u6696\u3044\u8f1d\u304d"),
    "moonlight": ("Moonlight", "\u6708\u5149", "\u30e0\u30fc\u30f3\u30e9\u30a4\u30c8",
                  "Cool dim directional night", "\u51b7\u8c03\u5fae\u5f31\u591c\u5149", "\u5bd2\u8272\u3067\u6de1\u3044\u591c\u306e\u5149"),
    "moonlit_win": ("Moonlit Window", "\u6708\u5149\u7a97", "\u6708\u5149\u306e\u7a93",
                    "Cool light through blinds", "\u767e\u53f6\u7a97\u51b7\u5149", "\u30d6\u30e9\u30a4\u30f3\u30c9\u8d8a\u3057\u306e\u5bd2\u5149"),
    "horror_up": ("Horror Uplight", "\u6050\u6016\u5e95\u5149", "\u30db\u30e9\u30fc\u4e0b\u5149",
                  "Green eerie underlight", "\u7eff\u8272\u8be1\u5f02\u5e95\u5149", "\u7dd1\u306e\u4e0d\u6c17\u5473\u306a\u4e0b\u5149"),
    "window": ("Window Light", "\u7a97\u5149", "\u7a93\u306e\u5149",
               "Soft directional window", "\u67d4\u548c\u65b9\u5411\u7a97\u5149", "\u67d4\u3089\u304b\u306a\u65b9\u5411\u7a93\u5149"),
    "window_blind": ("Window Blinds", "\u767e\u53f6\u7a97\u5149", "\u30d6\u30e9\u30a4\u30f3\u30c9",
                     "Striped blinds shadow", "\u767e\u53f6\u7a97\u6761\u7eb9\u5f71", "\u30d6\u30e9\u30a4\u30f3\u30c9\u306e\u7e1e\u6a21\u69d8"),
    "forest": ("Forest Dapple", "\u68ee\u6797\u6591\u5149", "\u6728\u6f0f\u308c\u65e5",
               "Green dappled foliage light", "\u7eff\u8272\u6811\u53f6\u6591\u9a73\u5149", "\u7dd1\u306e\u6728\u6f0f\u308c\u65e5"),
    "underwater": ("Underwater", "\u6c34\u4e0b", "\u6c34\u4e2d",
                   "Cyan caustic light", "\u9752\u7eff\u6c34\u4e0b\u6ce2\u5149", "\u30b7\u30a2\u30f3\u306e\u6c34\u4e2d\u5149"),
    "snow_bounce": ("Snow Bounce", "\u96ea\u5730\u53cd\u5149", "\u96ea\u306e\u53cd\u5c04",
                    "Bright cool with bottom fill", "\u660e\u4eae\u51b7\u8c03\u5e95\u8865\u5149", "\u660e\u308b\u3044\u5bd2\u8272\u3068\u4e0b\u88dc\u5149"),
    "desert": ("Desert", "\u6c99\u6f20", "\u7802\u6f20",
               "Hot warm bright sand", "\u708e\u70ed\u6696\u4eae\u6c99\u5730", "\u708e\u71b1\u3067\u660e\u308b\u3044\u7802"),
    "street_lamp": ("Street Lamp", "\u8857\u706f", "\u8857\u706f",
                    "Warm pool in darkness", "\u6697\u4e2d\u6696\u5149\u5149\u6c60", "\u6697\u95c7\u306e\u6696\u8272\u306e\u5149"),
    "stage_spot": ("Stage Spot", "\u821e\u53f0\u805a\u5149", "\u30b9\u30c6\u30fc\u30b8\u30b9\u30dd\u30c3\u30c8",
                   "Single hard spotlight", "\u5355\u4e2a\u786c\u805a\u5149\u706f", "\u5358\u4e00\u306e\u786c\u3044\u30b9\u30dd\u30c3\u30c8"),
    "concert_rgb": ("Concert RGB", "\u6f14\u5531\u4f1aRGB", "\u30b3\u30f3\u30b5\u30fcRGB",
                    "Colored stage spots", "\u5f69\u8272\u821e\u53f0\u805a\u5149", "\u30ab\u30e9\u30fc\u30b9\u30c6\u30fc\u30b8\u5149"),
    "sci_fi": ("Sci-Fi Panel", "\u79d1\u5e7b\u9762\u677f", "SF\u30d1\u30cd\u30eb",
               "Cool tech panel light", "\u51b7\u8c03\u79d1\u6280\u9762\u677f\u5149", "\u5bd2\u8272\u306e\u30c6\u30c3\u30af\u5149"),
}

for _rid, _v in _REF_I18N.items():
    TR[f"ref_{_rid}"] = {"EN": _v[0], "ZH": _v[1], "JA": _v[2]}
    TR[f"ref_{_rid}_desc"] = {"EN": _v[3], "ZH": _v[4], "JA": _v[5]}


# RNA property name -> translation key for tooltip sync.
_PROP_DESC = {
    "language": "desc_language",
    "reference_image": "desc_reference",
    "lighting_preset": "desc_lighting_preset",
    "reference_preset": "desc_reference_preset",
    "mode": "desc_mode",
    "target_mode": "desc_target",
    "orient_mode": "desc_orient",
    "use_luxpro": "desc_luxpro",
    "light_count": "desc_light_count",
    "color_strategy": "desc_color_strategy",
    "live": "desc_live",
    "intensity": "desc_intensity",
    "exposure": "desc_exposure",
    "auto_exposure": "desc_auto_exposure",
    "ae_speed": "desc_ae_speed",
    "ae_center_weight": "desc_ae_center_weight",
    "ae_gamma": "desc_ae_gamma",
    "distance": "desc_distance",
    "color_strength": "desc_color_strength",
    "color_saturation": "desc_color_saturation",
    "tone_shadows": "desc_tone_shadows",
    "tone_highlights": "desc_tone_highlights",
    "contrast_boost": "desc_contrast",
    "rig_rotation": "desc_rotate",
    "rig_height": "desc_height",
    "use_world": "desc_use_world",
    "timer_interval": "desc_timer_interval",
    "float_show": "desc_float_show",
    "float_opacity": "desc_float_opacity",
    "float_scale": "desc_float_scale",
    "lock_intensity": "desc_lock_intensity",
    "lock_exposure": "desc_lock_exposure",
    "lock_distance": "desc_lock_distance",
    "lock_rig_rotation": "desc_lock_rig_rotation",
    "lock_rig_height": "desc_lock_rig_height",
    "lock_color_strength": "desc_lock_color_strength",
    "lock_color_saturation": "desc_lock_color_saturation",
    "lock_tone_shadows": "desc_lock_tone_shadows",
    "lock_tone_highlights": "desc_lock_tone_highlights",
    "lock_contrast_boost": "desc_lock_contrast_boost",
}


def sync_descriptions(lang: str | None = None) -> None:
    """Register Blender UI translations for RNA tooltip strings (Blender 5.x RNA descriptions are read-only)."""
    try:
        import bpy
    except Exception:
        return
    trans = {"zh_CN": {}, "ja_JP": {}}
    for key, entry in TR.items():
        if not key.startswith("desc_"):
            continue
        src = entry.get("EN", "")
        if not src:
            continue
        if entry.get("ZH"):
            trans["zh_CN"][src] = entry["ZH"]
        if entry.get("JA"):
            trans["ja_JP"][src] = entry["JA"]
    try:
        bpy.app.translations.unregister(__name__)
    except Exception:
        pass
    try:
        bpy.app.translations.register(__name__, trans)
    except Exception:
        pass


def detect_language() -> str:
    """Map Blender's UI language to one of EN / ZH / JA."""
    try:
        import bpy
        code = (bpy.context.preferences.view.language or "").lower()
    except Exception:
        return "EN"
    if code.startswith("zh"):
        return "ZH"
    if code.startswith("ja"):
        return "JA"
    return "EN"


def tr(lang: str, key: str, **fmt) -> str:
    entry = TR.get(key)
    if not entry:
        text = key
    else:
        text = entry.get(lang) or entry.get("EN") or key
    if fmt:
        try:
            text = text.format(**fmt)
        except (KeyError, IndexError):
            pass
    return text


# Keep references to the lists returned by EnumProperty item callbacks, or
# Blender may garbage-collect the strings and crash.
_enum_cache: dict = {}


def _items(self, key_prefix, ids):
    lang = getattr(self, "language", "EN")
    items = [
        (ident, tr(lang, f"{key_prefix}_{suffix}"),
         tr(lang, f"{key_prefix}_{suffix}_desc"))
        for ident, suffix in ids
    ]
    _enum_cache[key_prefix] = items
    return items


def mode_items(self, context):
    return _items(self, "mode",
                  (("AUTO", "auto"), ("PORTRAIT", "portrait"), ("SCENE", "scene")))


def color_strategy_items(self, context):
    return _items(self, "color_strategy",
                  (("DEFAULT", "default"), ("VIVID", "vivid"), ("SOFT", "soft")))


def target_items(self, context):
    return _items(self, "target",
                  (("SELECTED", "selected"), ("CURSOR", "cursor"), ("ORIGIN", "origin")))


def orient_items(self, context):
    return _items(self, "orient",
                  (("CAMERA", "camera"), ("VIEW", "view")))


def corner_items(self, context):
    # BOTTOM_LEFT first so it is the default for new scenes.
    lang = getattr(self, "language", "EN")
    items = [
        ("BOTTOM_LEFT", tr(lang, "corner_bl"), ""),
        ("BOTTOM_RIGHT", tr(lang, "corner_br"), ""),
        ("TOP_LEFT", tr(lang, "corner_tl"), ""),
        ("TOP_RIGHT", tr(lang, "corner_tr"), ""),
    ]
    _enum_cache["corner"] = items
    return items
