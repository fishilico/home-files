KVIrc configuration
===================

KVIrc default configuration is quite good except the timestamp format of
messages. This format does not include the full date. The configuration
parameter which defines this lies in the following menu:
"Settings" -> "Configure Theme..." -> dialog "Text" -> tab "Timestamp" ->
field "Timestamp format:".

This format follows the QDateTime parsing format documented in
https://doc.qt.io/qt-5/qdatetime.html#fromString-1

``[ddd dd/MM hh:mm:ss]`` will the rendered as ``[Mon 04/02 12:34:56]``.
