/* Stub: secure_validator not present in the public Cherrygram source. */
#ifndef MYXAX_SECURE_VALIDATOR_STUB_HPP
#define MYXAX_SECURE_VALIDATOR_STUB_HPP

#include <jni.h>

namespace secure_validator {
    inline void maybeForceDisconnectOrUpdate(JNIEnv*, int, int) {}
    inline bool has_jni_hook(JNIEnv*) { return false; }
    inline bool has_xhook() { return false; }
    inline bool validate_signature(JNIEnv*) { return true; }
}

#endif
