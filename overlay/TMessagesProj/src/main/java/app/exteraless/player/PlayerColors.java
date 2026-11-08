package app.exteraless.player;

import org.telegram.ui.ActionBar.Theme;

/**
 * Small colour helper for the plugin install sheet.
 *
 * The upstream exteraless class builds a full Material 3 scheme with
 * MonetHelper. myxaxGram only needs a handful of theme-aware colours, so this
 * version maps them onto the current Telegram theme instead of pulling the
 * whole dynamic-colour stack into the build.
 */
public final class PlayerColors {

    public final boolean dark;

    public final int surface;
    public final int surfaceLow;
    public final int surfaceContainer;
    public final int surfaceHigh;
    public final int onSurface;
    public final int onSurfaceVariant;
    public final int outlineVariant;
    public final int primary;
    public final int onPrimary;
    public final int primaryContainer;
    public final int onPrimaryContainer;
    public final int secondaryContainer;
    public final int onSecondaryContainer;

    private PlayerColors(boolean dark) {
        this.dark = dark;
        surface = Theme.getColor(Theme.key_windowBackgroundWhite);
        surfaceLow = Theme.getColor(Theme.key_windowBackgroundGray);
        surfaceContainer = Theme.getColor(Theme.key_dialogBackground);
        surfaceHigh = Theme.getColor(Theme.key_actionBarDefault);
        onSurface = Theme.getColor(Theme.key_windowBackgroundWhiteBlackText);
        onSurfaceVariant = Theme.getColor(Theme.key_windowBackgroundWhiteGrayText);
        outlineVariant = Theme.getColor(Theme.key_divider);
        primary = Theme.getColor(Theme.key_featuredStickers_addButton);
        onPrimary = Theme.getColor(Theme.key_featuredStickers_buttonText);
        primaryContainer = Theme.getColor(Theme.key_featuredStickers_addButton);
        onPrimaryContainer = Theme.getColor(Theme.key_featuredStickers_buttonText);
        secondaryContainer = Theme.getColor(Theme.key_windowBackgroundWhite);
        onSecondaryContainer = Theme.getColor(Theme.key_windowBackgroundWhiteBlackText);
    }

    /**
     * Kept for signature compatibility with the upstream class. The seed is
     * intentionally ignored: plugin UI follows the active myxaxGram theme.
     */
    public static PlayerColors fromSeed(int seed, boolean dark) {
        return new PlayerColors(dark);
    }
}
