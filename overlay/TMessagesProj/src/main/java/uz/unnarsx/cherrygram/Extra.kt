package uz.unnarsx.cherrygram

/**
 * Stub for symbols that are not present in the public Cherrygram source at the
 * pinned commit. Values are inert defaults so the project can compile; the
 * features backed by these fields are effectively disabled.
 */
object Extra {
    @JvmField
    var VERIF_LOG: Boolean = false

    @JvmField
    val FILE_NAME_HASH: Array<String> = emptyArray()

    @JvmField
    val GITLAB_RAW_URL_HASH: Array<String> = emptyArray()

    @JvmField
    val FILE_NAME_MARKETPLACE_HASH: Array<String> = emptyArray()

    @JvmField
    val GITLAB_RAW_URL_MARKETPLACE_HASH: Array<String> = emptyArray()

    @JvmField
    val FILE_NAME_BLOCKED_HASH: Array<String> = emptyArray()

    @JvmField
    val GITLAB_RAW_URL_BLOCKED_HASH: Array<String> = emptyArray()

    @JvmField
    val FILE_NAME_BADGE_COLORS_HASH: Array<String> = emptyArray()

    @JvmField
    val GITLAB_RAW_URL_BADGE_COLORS_HASH: Array<String> = emptyArray()

    @JvmField
    val FILE_NAME_TON_RATE_HASH: Array<String> = emptyArray()
}
