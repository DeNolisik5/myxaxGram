# myxaxGram

**myxaxGram** — форк [Cherrygram](https://github.com/arsLan4k1390/Cherrygram) (Telegram 13.1.1 / Cherrygram 11.4.0) с интеграцией движка Python-плагинов [exteraless](https://github.com/exteraless/exteraless).

## Что делает проект

- Добавляет в настройки пункт **«Плагины»** строго между «Конфиденциальность» и «О myxaxGram».
- Встраивает рантайм плагинов exteraless: реестр/контроллер, движок Python (Chaquopy 17.0.0, Python 3.11), хуки (Aliuhook), разрешения, watchdog, UI установки и настроек плагинов.
- Сохраняет остальную функциональность оригинального Cherrygram.
- Сборка и подписание APK выполняются в **GitHub Actions**, готовый APK публикуется в **GitHub Releases**.

## Как устроена сборка

Этот репозиторий **не содержит** исходники Cherrygram/exteraless целиком. При каждой сборке workflow:

1. клонирует Cherrygram на закреплённом коммите;
2. забирает рантайм плагинов exteraless и форк Chaquopy на закреплённых коммитах;
3. накладывает `overlay/` и применяет патчи из `scripts/patch_cherrygram.py`;
4. собирает `TMessagesProj_AppStandalone` (flavor `afat`, build type `standalone`, ABI `arm64-v8a`);
5. подписывает APK ключом из секретов репозитория и публикует релиз.

Основные файлы интеграции:

- `scripts/integrate.sh` — сборка рабочего дерева исходников;
- `scripts/patch_cherrygram.py` — детерминированные правки Cherrygram;
- `overlay/` — адаптированные файлы движка/ресурсов;
- `.github/workflows/build.yml` — CI/CD.

## Секреты репозитория

Для подписи релиза в GitHub Actions должны быть заданы секреты:

- `RELEASE_KEYSTORE_BASE64` — keystore в base64;
- `RELEASE_STORE_PASSWORD`;
- `RELEASE_KEY_ALIAS`;
- `RELEASE_KEY_PASSWORD`.

Секреты и файлы ключей (`*.keystore`, `*.jks`, `.gh_token`) **не коммитятся**.

## Лицензия и происхождение

Проект основан на исходном коде Cherrygram/Telegram и компонентах exteraless/Chaquopy. Соблюдайте лицензии upstream-проектов и требования к распространению производных работ.
