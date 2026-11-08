#!/usr/bin/env python3
"""Patch a fresh Cherrygram checkout so it becomes myxaxGram.

Everything here is a deterministic text edit on upstream sources. The script
fails loudly when an anchor is missing, so a Cherrygram update cannot silently
produce a build without the plugin engine.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

changed: list[str] = []


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing file: {rel}")
    return path.read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding="utf-8")
    changed.append(rel)


def sub_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    if old not in text:
        fail(f"{rel}: anchor not found:\n{old[:200]}")
    if text.count(old) != 1:
        fail(f"{rel}: anchor is not unique ({text.count(old)} matches)")
    write(rel, text.replace(old, new))


def append_once(rel: str, block: str, marker: str) -> None:
    text = read(rel)
    if marker in text:
        return
    if not text.endswith("\n"):
        text += "\n"
    write(rel, text + "\n" + block)


def sub_if_present(rel: str, old: str, new: str) -> bool:
    path = ROOT / rel
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if old not in text:
        return False
    if new in text and old not in text.replace(new, ""):
        # already patched form exists
        return True
    path.write_text(text.replace(old, new), encoding="utf-8")
    changed.append(rel)
    return True


# --------------------------------------------------------------------------
# Gradle wiring
# --------------------------------------------------------------------------

sub_once(
    "settings.gradle",
    """dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}""",
    """dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        // Aliuhook (Xposed-compatible hooks on top of LSPlant).
        maven { url 'https://maven.aliucord.com/releases' }
    }
}""",
)

sub_once(
    "build.gradle",
    "        classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:2.2.0'\n",
    "        classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:2.2.0'\n"
    "        classpath 'com.chaquo.python:gradle:17.0.0'\n",
)

sub_once(
    "build.gradle",
    """        maven { url 'https://developer.huawei.com/repo/' }
        maven { url "https://jitpack.io" }""",
    """        maven { url 'https://developer.huawei.com/repo/' }
        maven { url "https://jitpack.io" }
        maven { url 'https://maven.aliucord.com/releases' }""",
)

sub_once(
    "gradle.properties",
    "APP_PACKAGE=uz.unnarsx.cherrygram",
    "APP_PACKAGE=myxax.gram",
)
sub_once(
    "gradle.properties",
    "APP_VERSION_NAME_CHERRY=11.4.0",
    "APP_VERSION_NAME_CHERRY=1.0.0",
)

# Chaquopy fails if the build machine runs a different Python minor version
# than the app. Keep the Gradle daemon from swallowing all runner memory.
sub_once(
    "gradle.properties",
    "org.gradle.jvmargs=-Xmx8g -XX:MaxMetaspaceSize=1g",
    "org.gradle.jvmargs=-Xmx6g -XX:MaxMetaspaceSize=1g",
)

# --------------------------------------------------------------------------
# TMessagesProj (library module): Python runtime + BuildConfig fields
# --------------------------------------------------------------------------

sub_once(
    "TMessagesProj/build.gradle",
    "apply plugin: 'com.android.library'\napply plugin: 'kotlin-android'",
    "apply plugin: 'com.android.library'\napply plugin: 'kotlin-android'\n"
    "// myxaxGram: Python plugin runtime (Chaquopy).\n"
    "apply from: file('myxax/chaquopy.gradle')",
)

sub_once(
    "TMessagesProj/build.gradle",
    '        buildConfigField "String", "GET_BUILD_DATE", "\\"${getCurrentDate()}\\""\n',
    '        buildConfigField "String", "GET_BUILD_DATE", "\\"${getCurrentDate()}\\""\n'
    '        buildConfigField "boolean", "DEBUG_TOOLS", "false"\n'
    '        buildConfigField "String", "BUILD_COMMIT_ID", '
    '"\\"${System.getenv(\'GITHUB_SHA\') ?: \'\'}\\""\n',
)

PLUGIN_PROGUARD = """
# --- myxaxGram plugin engine -----------------------------------------------
# Everything below is reached from Python through Chaquopy reflection, which
# static analysis cannot see. R8 would strip it from the release APK.
-keep class app.exteraless.plugins.** { *; }
-keep class app.exteraless.debug.** { *; }
-keep class app.exteraless.player.** { *; }
-keep class app.exteraless.utils.** { *; }
-keep class com.exteragram.messenger.** { *; }
-keep class de.robv.android.xposed.** { *; }
-keep class com.aliucord.** { *; }
-keep class org.mvel2.** { *; }
-keep class com.android.dx.** { *; }
-dontwarn com.android.dx.**
-dontwarn org.mvel2.**
-keepclassmembers class org.telegram.tgnet.** { *; }
-keepclassmembers class org.telegram.messenger.MessageObject { *; }
-keepclassmembers class org.telegram.messenger.SendMessagesHelper { *; }
-keepclassmembers class org.telegram.messenger.BuildVars { *; }
-keep class * extends org.telegram.ui.Components.UItem$UItemFactory { public <init>(...); }
"""
append_once("TMessagesProj/proguard-rules.pro", PLUGIN_PROGUARD, "app.exteraless.plugins.**")

# --------------------------------------------------------------------------
# Standalone app module: signing, single ABI, no splits
# --------------------------------------------------------------------------

sub_once(
    "TMessagesProj_AppStandalone/build.gradle",
    """    signingConfigs {
        debug {
            storeFile file('../Your_Key.jks')
            storePassword 'Your_Password'
            keyAlias 'Your_Alias'
            keyPassword 'Your_Password'
        }

        release {
            storeFile file('../Your_Key.jks')
            storePassword 'Your_Password'
            keyAlias 'Your_Alias'
            keyPassword 'Your_Password'
        }
    }""",
    """    signingConfigs {
        debug {
            storeFile rootProject.file(System.getenv('RELEASE_STORE_FILE') ?: 'release.keystore')
            storePassword System.getenv('RELEASE_STORE_PASSWORD') ?: 'android'
            keyAlias System.getenv('RELEASE_KEY_ALIAS') ?: 'androidkey'
            keyPassword System.getenv('RELEASE_KEY_PASSWORD') ?: 'android'
        }

        release {
            storeFile rootProject.file(System.getenv('RELEASE_STORE_FILE') ?: 'release.keystore')
            storePassword System.getenv('RELEASE_STORE_PASSWORD') ?: 'android'
            keyAlias System.getenv('RELEASE_KEY_ALIAS') ?: 'androidkey'
            keyPassword System.getenv('RELEASE_KEY_PASSWORD') ?: 'android'
        }
    }""",
)

sub_once(
    "TMessagesProj_AppStandalone/build.gradle",
    'abiFilters "armeabi-v7a", "arm64-v8a"/*, "x86", "x86_64"*/',
    'abiFilters "arm64-v8a"',
)

sub_once(
    "TMessagesProj_AppStandalone/build.gradle",
    """    splits.abi {
        enable true
        reset()
        //noinspection ChromeOsAbiSupport
        include "arm64-v8a", "armeabi-v7a"
        universalApk true
    }""",
    """    // ndk.abiFilters is set per flavor; splits.abi conflicts with it in AGP 8.x.
    splits.abi {
        enable false
    }""",
)

sub_once(
    "TMessagesProj_AppStandalone/build.gradle",
    'outputFileName = "Cherrygram-${APP_VERSION_NAME_CHERRY}-TG-${defaultConfig.versionName}-${abi}.apk"',
    'outputFileName = "myxaxGram-${APP_VERSION_NAME_CHERRY}-TG-${defaultConfig.versionName}-${abi}.apk"',
)

import re

CI_ENV_OLD = """def env = loadEnv("${project.rootDir}/secrets_for_ci.env")
env.each { key, value ->
    ext."$key" = value
}"""
CI_ENV_NEW = """def ciEnvFile = new File("${project.rootDir}/secrets_for_ci.env")
def env = ciEnvFile.exists() ? loadEnv(ciEnvFile.path) : [:]
env.each { key, value ->
    ext."$key" = value
}"""
CI_ENV_RE = re.compile(
    r'def\s+env\s*=\s*loadEnv\(\s*"\$\{project\.rootDir\}/secrets_for_ci\.env"\s*\)\s*'
    r'env\.each\s*\{\s*key\s*,\s*value\s*->\s*ext\."\$key"\s*=\s*value\s*\}',
    re.S,
)

for gradle in sorted(ROOT.glob("TMessagesProj_App*/build.gradle")):
    rel = str(gradle.relative_to(ROOT))
    if sub_if_present(rel, CI_ENV_OLD, CI_ENV_NEW):
        continue
    text = gradle.read_text(encoding="utf-8")
    if 'secrets_for_ci.env' not in text or 'ciEnvFile' in text:
        continue
    new, n = CI_ENV_RE.subn(CI_ENV_NEW, text)
    if n:
        gradle.write_text(new, encoding="utf-8")
        changed.append(rel)

# --------------------------------------------------------------------------
# Settings screen: "Plugins" strictly between privacy and about
# --------------------------------------------------------------------------

PREFERENCES = "TMessagesProj/src/main/java/uz/unnarsx/cherrygram/preferences/CGPreferencesEntry.java"

sub_once(
    PREFERENCES,
    "    private final int aboutRow = 7;",
    "    private final int aboutRow = 7;\n"
    "    private final int pluginsRow = 11;",
)

sub_once(
    PREFERENCES,
    """        items.add(
                SettingsActivity.SettingCell.Factory.of(
                        aboutRow,""",
    """        items.add(
                SettingsActivity.SettingCell.Factory.of(
                        pluginsRow,
                        IconBackgroundColors.PURPLE.top, IconBackgroundColors.PURPLE.bottom,
                        R.drawable.msg_plugins,
                        getString(R.string.CGP_Plugins),
                        getString(R.string.CGP_Plugins_Desc),
                        true
                )
        );
        items.add(
                SettingsActivity.SettingCell.Factory.of(
                        aboutRow,""",
)

sub_once(
    PREFERENCES,
    """        } else if (item.id == aboutRow) {
            CherrygramPreferencesNavigator.INSTANCE.createAbout(this);""",
    """        } else if (item.id == pluginsRow) {
            presentFragment(new app.exteraless.plugins.ui.PluginsActivity());
        } else if (item.id == aboutRow) {
            CherrygramPreferencesNavigator.INSTANCE.createAbout(this);""",
)

# --------------------------------------------------------------------------
# Application startup
# --------------------------------------------------------------------------

APPLICATION_LOADER = "TMessagesProj/src/main/java/org/telegram/messenger/ApplicationLoader.java"

sub_once(
    APPLICATION_LOADER,
    "import uz.unnarsx.cherrygram.misc.widgets.KaboomWidget;\n",
    "import uz.unnarsx.cherrygram.misc.widgets.KaboomWidget;\n"
    "\nimport app.exteraless.plugins.PluginsController;\n",
)

sub_once(
    APPLICATION_LOADER,
    """    private void initCG() {
        KaboomWidget.forceUpdateKaboomWidgets(applicationContext);""",
    """    private void initCG() {
        // Starts the Python engine; the controller does the heavy work in the
        // background so the first frame is not delayed.
        PluginsController.getInstance().init(applicationContext);
        KaboomWidget.forceUpdateKaboomWidgets(applicationContext);""",
)

# --------------------------------------------------------------------------
# Strings: app name and the new settings row
# --------------------------------------------------------------------------

sub_once(
    "TMessagesProj/src/main/res-cherrygram/values/cg_strings.xml",
    '<string name="CG_AppName" translatable="false">Cherrygram</string>',
    '<string name="CG_AppName" translatable="false">myxaxGram</string>',
)

# --------------------------------------------------------------------------
# Firebase: the client entry has to match the new application id
# --------------------------------------------------------------------------

for rel in (
    "TMessagesProj/google-services.json",
    "TMessagesProj/src/google-services.json",
    "TMessagesProj_AppStandalone/google-services.json",
):
    path = ROOT / rel
    if not path.is_file():
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    touched = False
    for client in data.get("client", []):
        info = client.get("client_info", {}).get("android_client_info", {})
        if info.get("package_name") == "uz.unnarsx.cherrygram":
            info["package_name"] = "myxax.gram"
            touched = True
        for oauth in client.get("oauth_client", []):
            android = oauth.get("android_info") or {}
            if android.get("package_name") == "uz.unnarsx.cherrygram":
                android["package_name"] = "myxax.gram"
                touched = True
    if touched:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        changed.append(rel)

# --------------------------------------------------------------------------
# Ported plugin sources: drop NagramX / exteraless-only leaf dependencies
# --------------------------------------------------------------------------

PLUGINS_JAVA = "TMessagesProj/src/main/java/app/exteraless/plugins"

sub_once(
    f"{PLUGINS_JAVA}/PluginsWatchdog.java",
    "import tw.nekomimi.nekogram.helpers.AppRestartHelper;",
    "import uz.unnarsx.cherrygram.core.helpers.AppRestartHelper;",
)
sub_once(
    f"{PLUGINS_JAVA}/PluginsWatchdog.java",
    "AppRestartHelper.triggerRebirth(activity, new Intent(activity, LaunchActivity.class));",
    "AppRestartHelper.restartApp(activity);",
)

for rel in (
    f"{PLUGINS_JAVA}/ui/PluginsActivity.java",
    f"{PLUGINS_JAVA}/ui/PluginActivityLogActivity.java",
):
    text = read(rel)
    if "tw.nekomimi.nekogram.utils.ShareUtil.shareFile(activity, file);" not in text:
        fail(f"{rel}: ShareUtil call not found")
    text = text.replace(
        "tw.nekomimi.nekogram.utils.ShareUtil.shareFile(activity, file);",
        "app.exteraless.plugins.ui.PluginShare.shareFile(activity, file);",
    )
    write(rel, text)

sub_once(
    f"{PLUGINS_JAVA}/ui/PluginsActivity.java",
    "R.drawable.ic_ab_search_solar",
    "R.drawable.outline_header_search",
)

print("patched files:")
for rel in changed:
    print(f"  {rel}")
