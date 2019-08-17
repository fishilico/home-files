Install Rust compiler with Rustup
=================================

Install commands in order to install a stable toolchain with ``rustup`` (as advised by https://anssi-fr.github.io/rust-guide/02_devenv.html):

.. code-block:: sh

    rustup toolchain install stable
    rustup default stable
    rustup update

    # Install:
    # * rustfmt for "cargo fmt"
    # * clippy to catch common mistakes
    # * cargo-outdated to display out-of-date Rust dependencies
    # * cargo-audit to easily check for security vulnerabilities reported to the RustSec Advisory Database
    rustup component add rustfmt
    rustup component add clippy
    cargo install cargo-outdated
    cargo install cargo-audit

Then, building, testing and running a Rsut project is a mater of:

.. code-block:: sh

    cargo fmt
    cargo build
    cargo test
    cargo run
    cargo build --release

In order to build a Rust project as statically-linked executable, a Musl target can be installed:

.. code-block:: sh

    rustup target add x86_64-unknown-linux-musl
    cargo build --release --target x86_64-unknown-linux-musl

In order to cross-compile for other architectures such as ARM:

.. code-block:: sh

    rustup target add arm-unknown-linux-gnueabi
    cargo build --release --target arm-unknown-linux-gnueabi

Or to cross-compile for Windows:

.. code-block:: sh

    # Windows x86-64
    rustup target add x86_64-pc-windows-gnu
    cargo build --release --target x86_64-pc-windows-gnu

    # Windows x86-32
    rustup target add i686-pc-windows-gnu
    cargo build --release --target i686-pc-windows-gnu

    # If it fails, follow instructions from https://wiki.archlinux.org/index.php/Rust#Windows
    for LIB in crt2.o dllcrt2.o libmsvcrt.a; do
        for CHANNELDIR in "$HOME/.rustup/toolchains/"*-linux-gnu/lib/rustlib/x86_64-pc-windows-gnu; do
            cp -v "/usr/x86_64-w64-mingw32/lib/$LIB" "$CHANNELDIR/lib/";
        done;
        for CHANNELDIR in "$HOME/.rustup/toolchains/"*-linux-gnu/lib/rustlib/i686-pc-windows-gnu; do
            cp -v "/usr/i686-w64-mingw32/lib/$LIB" "$CHANNELDIR/lib/";
        done;
    done

    # Register Wine to run Windows executables automatically
    echo ':DOSWin:M::MZ::/usr/bin/wine:' > /proc/sys/fs/binfmt_misc/register
