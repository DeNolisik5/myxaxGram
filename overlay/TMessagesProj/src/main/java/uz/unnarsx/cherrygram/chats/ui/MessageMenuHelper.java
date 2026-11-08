package uz.unnarsx.cherrygram.chats.ui;

import android.graphics.Canvas;
import android.view.View;

import org.telegram.messenger.UserConfig;
import org.telegram.ui.ActionBar.Theme;

/**
 * Stub for a class missing from the public Cherrygram source at the pinned
 * commit. Methods return safe defaults so the app compiles; advanced message
 * menu customisations provided by that class are disabled.
 */
public class MessageMenuHelper {

    private static final MessageMenuHelper[] Instance = new MessageMenuHelper[UserConfig.MAX_ACCOUNT_COUNT];

    public static MessageMenuHelper getInstance(int currentAccount) {
        MessageMenuHelper local = Instance[currentAccount];
        if (local == null) {
            synchronized (MessageMenuHelper.class) {
                local = Instance[currentAccount];
                if (local == null) {
                    local = Instance[currentAccount] = new MessageMenuHelper();
                }
            }
        }
        return local;
    }

    public boolean allowNewMessageMenu() {
        return false;
    }

    public boolean showDivider() {
        return false;
    }

    public boolean showCustomDivider(boolean value) {
        return false;
    }

    public void drawCopyInChat(Canvas canvas, View view) {
    }

    public static int getMessageMenuBackgroundColor(Theme.ResourcesProvider resourcesProvider) {
        return Theme.getColor(Theme.key_actionBarDefaultSubmenuBackground, resourcesProvider);
    }

    public static int getMessageMenuGapColor(Theme.ResourcesProvider resourcesProvider) {
        return Theme.getColor(Theme.key_actionBarDefaultSubmenuSeparator, resourcesProvider);
    }
}
