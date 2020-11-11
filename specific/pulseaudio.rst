PulseAudio user settings
========================

To list cards and available output profiles:

.. code-block:: console

    $ pacmd list-cards
    1 card(s) available.
        index: 0
            name: <alsa_card.pci-0000_00_1f.3>
            driver: <module-alsa-card.c>
            owner module: 24
            properties:
                alsa.card = "0"
                alsa.card_name = "HDA Intel PCH"
                alsa.long_card_name = "HDA Intel PCH at 0xc973c000 irq 166"
                alsa.driver_name = "snd_hda_intel"
                device.bus_path = "pci-0000:00:1f.3"
                sysfs.path = "/devices/pci0000:00/0000:00:1f.3/sound/card0"
                device.bus = "pci"
                device.vendor.id = "8086"
                device.vendor.name = "Intel Corporation"
                device.product.id = "9dc8"
                device.product.name = "Cannon Point-LP High Definition Audio Controller"
                device.form_factor = "internal"
                device.string = "0"
                device.description = "Built-in Audio"
                module-udev-detect.discovered = "1"
                device.icon_name = "audio-card-pci"
            profiles:
                input:analog-stereo: Analog Stereo Input (priority 65, available: unknown)
                output:analog-stereo: Analog Stereo Output (priority 6500, available: unknown)
                output:analog-stereo+input:analog-stereo: Analog Stereo Duplex (priority 6565, available: unknown)
                output:hdmi-stereo: Digital Stereo (HDMI) Output (priority 5900, available: unknown)
                output:hdmi-stereo+input:analog-stereo: Digital Stereo (HDMI) Output + Analog Stereo Input (priority 5965, available: unknown)
                output:hdmi-surround: Digital Surround 5.1 (HDMI) Output (priority 800, available: unknown)
                output:hdmi-surround+input:analog-stereo: Digital Surround 5.1 (HDMI) Output + Analog Stereo Input (priority 865, available: unknown)
                output:hdmi-surround71: Digital Surround 7.1 (HDMI) Output (priority 800, available: unknown)
                output:hdmi-surround71+input:analog-stereo: Digital Surround 7.1 (HDMI) Output + Analog Stereo Input (priority 865, available: unknown)
                output:hdmi-stereo-extra1: Digital Stereo (HDMI 2) Output (priority 5700, available: unknown)
                output:hdmi-stereo-extra1+input:analog-stereo: Digital Stereo (HDMI 2) Output + Analog Stereo Input (priority 5765, available: unknown)
                output:hdmi-surround-extra1: Digital Surround 5.1 (HDMI 2) Output (priority 600, available: unknown)
                output:hdmi-surround-extra1+input:analog-stereo: Digital Surround 5.1 (HDMI 2) Output + Analog Stereo Input (priority 665, available: unknown)
                output:hdmi-surround71-extra1: Digital Surround 7.1 (HDMI 2) Output (priority 600, available: unknown)
                output:hdmi-surround71-extra1+input:analog-stereo: Digital Surround 7.1 (HDMI 2) Output + Analog Stereo Input (priority 665, available: unknown)
                output:hdmi-stereo-extra2: Digital Stereo (HDMI 3) Output (priority 5700, available: no)
                output:hdmi-stereo-extra2+input:analog-stereo: Digital Stereo (HDMI 3) Output + Analog Stereo Input (priority 5765, available: no)
                output:hdmi-surround-extra2: Digital Surround 5.1 (HDMI 3) Output (priority 600, available: no)
                output:hdmi-surround-extra2+input:analog-stereo: Digital Surround 5.1 (HDMI 3) Output + Analog Stereo Input (priority 665, available: no)
                output:hdmi-surround71-extra2: Digital Surround 7.1 (HDMI 3) Output (priority 600, available: no)
                output:hdmi-surround71-extra2+input:analog-stereo: Digital Surround 7.1 (HDMI 3) Output + Analog Stereo Input (priority 665, available: no)
                output:hdmi-stereo-extra3: Digital Stereo (HDMI 4) Output (priority 5700, available: no)
                output:hdmi-stereo-extra3+input:analog-stereo: Digital Stereo (HDMI 4) Output + Analog Stereo Input (priority 5765, available: no)
                output:hdmi-surround-extra3: Digital Surround 5.1 (HDMI 4) Output (priority 600, available: no)
                output:hdmi-surround-extra3+input:analog-stereo: Digital Surround 5.1 (HDMI 4) Output + Analog Stereo Input (priority 665, available: no)
                output:hdmi-surround71-extra3: Digital Surround 7.1 (HDMI 4) Output (priority 600, available: no)
                output:hdmi-surround71-extra3+input:analog-stereo: Digital Surround 7.1 (HDMI 4) Output + Analog Stereo Input (priority 665, available: no)
                output:hdmi-stereo-extra4: Digital Stereo (HDMI 5) Output (priority 5700, available: no)
                output:hdmi-stereo-extra4+input:analog-stereo: Digital Stereo (HDMI 5) Output + Analog Stereo Input (priority 5765, available: no)
                output:hdmi-surround-extra4: Digital Surround 5.1 (HDMI 5) Output (priority 600, available: no)
                output:hdmi-surround-extra4+input:analog-stereo: Digital Surround 5.1 (HDMI 5) Output + Analog Stereo Input (priority 665, available: no)
                output:hdmi-surround71-extra4: Digital Surround 7.1 (HDMI 5) Output (priority 600, available: no)
                output:hdmi-surround71-extra4+input:analog-stereo: Digital Surround 7.1 (HDMI 5) Output + Analog Stereo Input (priority 665, available: no)
                off: Off (priority 0, available: unknown)
            active profile: <output:hdmi-stereo-extra1>
            sinks:
                alsa_output.pci-0000_00_1f.3.hdmi-stereo-extra1/#18: Built-in Audio Digital Stereo (HDMI 2)
            sources:
                alsa_output.pci-0000_00_1f.3.hdmi-stereo-extra1.monitor/#19: Monitor of Built-in Audio Digital Stereo (HDMI 2)
            ports:
                analog-input-internal-mic: Internal Microphone (priority 8900, latency offset 0 usec, available: unknown)
                    properties:
                        device.icon_name = "audio-input-microphone"
                analog-input-mic: Microphone (priority 8700, latency offset 0 usec, available: no)
                    properties:
                        device.icon_name = "audio-input-microphone"
                analog-output-speaker: Speakers (priority 10000, latency offset 0 usec, available: unknown)
                    properties:
                        device.icon_name = "audio-speakers"
                analog-output-headphones: Headphones (priority 9900, latency offset 0 usec, available: no)
                    properties:
                        device.icon_name = "audio-headphones"
                hdmi-output-0: HDMI / DisplayPort (priority 5900, latency offset 0 usec, available: yes)
                    properties:
                        device.icon_name = "video-display"
                        device.product.name = "L222W"
                hdmi-output-1: HDMI / DisplayPort 2 (priority 5800, latency offset 0 usec, available: yes)
                    properties:
                        device.icon_name = "video-display"
                        device.product.name = "C27F390"
                hdmi-output-2: HDMI / DisplayPort 3 (priority 5700, latency offset 0 usec, available: no)
                    properties:
                        device.icon_name = "video-display"
                hdmi-output-3: HDMI / DisplayPort 4 (priority 5600, latency offset 0 usec, available: no)
                    properties:
                        device.icon_name = "video-display"
                hdmi-output-4: HDMI / DisplayPort 5 (priority 5500, latency offset 0 usec, available: no)
                    properties:
                        device.icon_name = "video-display"

To change the current profile, in such a configuration:

.. code-block:: sh

    # To use "Analog Stereo Duplex"
    pacmd set-card-profile 0 output:analog-stereo+input:analog-stereo
    # ... or
    pacmd set-card-profile alsa_card.pci-0000_00_1f.3 output:analog-stereo+input:analog-stereo

    # To use "Digital Stereo (HDMI 2) Output"
    pacmd set-card-profile alsa_card.pci-0000_00_1f.3 output:hdmi-stereo-extra1

System configuration and networking is documented on https://fishilico.github.io/generic-config/sysadmin/sound.html
