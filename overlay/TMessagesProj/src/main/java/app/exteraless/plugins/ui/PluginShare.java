package app.exteraless.plugins.ui;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;

import androidx.core.content.FileProvider;

import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.FileLog;
import org.telegram.messenger.LocaleController;
import org.telegram.messenger.R;

import java.io.File;
import java.util.Locale;

/**
 * Shares plugin logs and backups through the system chooser.
 *
 * exteraless uses NagramX's {@code tw.nekomimi.nekogram.utils.ShareUtil}; myxaxGram
 * is built on Cherrygram, which does not ship that class. The Telegram manifest
 * already declares a {@code FileProvider} at {@code <applicationId>.provider}
 * whose paths cover both the logs and the cache directories, so the same
 * behaviour is reproduced here without touching the manifest.
 */
public final class PluginShare {

    private PluginShare() {
    }

    public static void shareFile(Activity activity, File file) {
        if (activity == null || file == null || !file.isFile()) {
            return;
        }
        try {
            final Uri uri = FileProvider.getUriForFile(activity,
                    ApplicationLoader.getApplicationId() + ".provider", file);
            final String name = file.getName().toLowerCase(Locale.US);
            final String type;
            if (name.endsWith(".log") || name.endsWith(".txt")) {
                type = "text/plain";
            } else if (name.endsWith(".zip")) {
                type = "application/zip";
            } else {
                type = "application/octet-stream";
            }
            final Intent intent = new Intent(Intent.ACTION_SEND);
            intent.setType(type);
            intent.putExtra(Intent.EXTRA_STREAM, uri);
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            activity.startActivity(Intent.createChooser(intent,
                    LocaleController.getString(R.string.PluginsShare)));
        } catch (Throwable e) {
            FileLog.e(e);
        }
    }
}
