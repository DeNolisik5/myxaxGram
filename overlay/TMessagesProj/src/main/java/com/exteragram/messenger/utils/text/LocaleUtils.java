package com.exteragram.messenger.utils.text;

import android.text.SpannableStringBuilder;
import android.text.TextUtils;
import android.text.style.URLSpan;

import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.Components.URLSpanNoUnderline;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Minimal stand-in for exteraGram's LocaleUtils, used by the plugin UI.
 *
 * The original class depends on exteraless-only helpers (TypefaceHelper,
 * LinkedCustomEmoji, FilterCreateActivity). The plugin subsystem only needs
 * plain text formatting plus the application name, so this version keeps the
 * public surface the plugin code calls and drops the rest.
 */
public final class LocaleUtils {

    private static final Pattern MARKDOWN_LINK_PATTERN =
            Pattern.compile("\\[([^]]+?)]\\(([^)\\s]+)\\)");

    private LocaleUtils() {
    }

    public static String getAppName() {
        try {
            return ApplicationLoader.applicationContext.getString(R.string.CG_AppName);
        } catch (Exception ignore) {
            return "myxaxGram";
        }
    }

    public static String getActionBarTitle() {
        return getAppName();
    }

    public static String ensureUrlHasHttps(String url) {
        if (url == null) {
            return null;
        }
        if (url.contains("://")) {
            return url;
        }
        return AndroidUtilities.WEB_URL != null && AndroidUtilities.WEB_URL.matcher(url).matches()
                ? "https://".concat(url) : url;
    }

    public static CharSequence formatWithURLs(CharSequence text) {
        if (TextUtils.isEmpty(text) || AndroidUtilities.WEB_URL == null) {
            return text;
        }
        SpannableStringBuilder builder = new SpannableStringBuilder(text);
        Matcher matcher = AndroidUtilities.WEB_URL.matcher(text);
        while (matcher.find()) {
            try {
                builder.setSpan(new URLSpanNoUnderline(ensureUrlHasHttps(matcher.group(0))),
                        matcher.start(), matcher.end(), SpannableStringBuilder.SPAN_EXCLUSIVE_EXCLUSIVE);
            } catch (Exception ignore) {
            }
        }
        return builder;
    }

    public static CharSequence formatWithUsernames(CharSequence text) {
        return text;
    }

    public static CharSequence formatWithUsernames(CharSequence text, BaseFragment fragment) {
        return text;
    }

    public static CharSequence formatWithUsernames(CharSequence text, BaseFragment fragment,
                                                   Runnable onClick) {
        return text;
    }

    public static CharSequence fullyFormatText(CharSequence text) {
        return fullyFormatText(text, null, null);
    }

    public static CharSequence fullyFormatText(CharSequence text, BaseFragment fragment,
                                               Runnable onClick) {
        if (TextUtils.isEmpty(text)) {
            return text;
        }
        CharSequence formatted = AndroidUtilities.replaceTags(text);
        return formatWithHTMLURLs(formatted);
    }

    public static CharSequence formatWithHtmlURLs(CharSequence text) {
        if (TextUtils.isEmpty(text)) {
            return text;
        }
        SpannableStringBuilder builder = new SpannableStringBuilder(text);
        URLSpan[] spans = builder.getSpans(0, builder.length(), URLSpan.class);
        for (URLSpan span : spans) {
            int start = builder.getSpanStart(span);
            int end = builder.getSpanEnd(span);
            String url = span.getURL();
            builder.removeSpan(span);
            builder.setSpan(new URLSpanNoUnderline(url), start, end,
                    SpannableStringBuilder.SPAN_EXCLUSIVE_EXCLUSIVE);
        }
        return builder;
    }
}
