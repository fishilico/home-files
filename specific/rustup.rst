Install Rust compiler with Rustup
=================================

Basic setup
-----------

Install commands in order to install a stable toolchain with ``rustup`` (as advised by https://anssi-fr.github.io/rust-guide/02_devenv.html):

.. code-block:: sh

    rustup toolchain install stable
    rustup default stable
    rustup update

    # Install:
    # * rustfmt for "cargo fmt"
    # * clippy to catch common mistakes
    # * llvm-tools to enable generating profiling data
    # * cargo-outdated to display out-of-date Rust dependencies
    # * cargo-audit to easily check for security vulnerabilities reported to the RustSec Advisory Database
    # * cargo-deps to graph the dependencies of a project
    # * cargo-geiger to list the dependencies with unsafe code
    # * cargo-tarpaulin to report the code coverage of tests (with "cargo tarpaulin -v -o Html")
    # * cargo-asm to view the generated ASM code (with "cargo asm --asm-style=intel --rust my_crate::my_function")
    rustup component add rustfmt
    rustup component add clippy
    rustup component add llvm-tools
    cargo install cargo-outdated
    cargo install cargo-audit
    cargo install cargo-deps
    cargo install cargo-geiger
    cargo install cargo-tarpaulin
    cargo install cargo-asm

    # Install tools only available with a nightly compiler
    # * cargo-fuzz to perform fuzzing (with llvm-dev on Debian to view symbols with llvm-symbolizer)
    #   doc for coverage: https://rust-fuzz.github.io/book/cargo-fuzz/coverage.html
    rustup toolchain install nightly
    rustup component add --toolchain nightly llvm-tools
    cargo install cargo-fuzz

    # Install miri to catch issues in Rust's mid-level intermediate representation (MIR)
    MIRI_NIGHTLY="nightly-$(curl -s https://rust-lang.github.io/rustup-components-history/x86_64-unknown-linux-gnu/miri)"
    rustup toolchain install "$MIRI_NIGHTLY"
    rustup component add --toolchain="$MIRI_NIGHTLY" miri

When using nightly instead of stable, the available Rustup components are documented on https://rust-lang.github.io/rustup-components-history/.

In order to work on a project (build, run, test, etc.), here are some commands.

.. code-block:: sh

    # Build, test and run
    cargo build
    cargo test
    cargo run

    # Build in release mode
    cargo build --release

    # Reformat the source files according to Rust's best practices
    cargo fmt

    # Check whether the files are formatted correctly (--check in nightly)
    cargo fmt --all -- --write-mode=diff

    # Lint the code
    cargo clippy --all-targets --all-features

    # Show the expanded macro definitions of a file
    ~/.rustup/toolchains/nightly-$(uname -m)-unknown-linux-gnu/bin/rustc --pretty=expanded -Z unstable-options file.rs

    # Graph the dependencies of a project
    cargo deps --all-deps | dot -Tsvg > cargo-deps.svg
    cargo deps --all-deps | xdot -

    # Build the documentation of a project, including the private types
    # and excluding the dependencies
    cargo doc --no-deps --document-private-items


Other targets
-------------

In order to build a Rust project as statically-linked executable on Linux, a Musl target can be installed:

.. code-block:: sh

    rustup target add x86_64-unknown-linux-musl
    cargo build --release --target x86_64-unknown-linux-musl

Rust can be compiled to many architectures. In order to list all the supported ones, several methods exist:

* by running ``rustup target list``
* by running ``rustc --print target-list``
* by browsing https://rust-lang.github.io/rustup-components-history/

In order to cross-compile for other architectures such as ARM:

.. code-block:: sh

    rustup target add arm-unknown-linux-gnueabi
    cargo build --release --target arm-unknown-linux-gnueabi

To cross-compile a project for Windows, from a system that has MinGW-w64:

.. code-block:: sh

    # Windows x86-64
    rustup target add x86_64-pc-windows-gnu
    cargo build --release --target x86_64-pc-windows-gnu

    # Windows x86-32
    rustup target add i686-pc-windows-gnu
    cargo build --release --target i686-pc-windows-gnu

    # If it fails, follow instructions from https://wiki.archlinux.org/title/Rust#Windows
    for LIB in crt2.o dllcrt2.o libmsvcrt.a; do
        for CHANNELDIR in "$HOME/.rustup/toolchains/"*-linux-gnu/lib/rustlib/x86_64-pc-windows-gnu; do
            cp -v "/usr/x86_64-w64-mingw32/lib/$LIB" "$CHANNELDIR/lib/";
        done;
        for CHANNELDIR in "$HOME/.rustup/toolchains/"*-linux-gnu/lib/rustlib/i686-pc-windows-gnu; do
            cp -v "/usr/i686-w64-mingw32/lib/$LIB" "$CHANNELDIR/lib/";
        done;
    done

    # Register Wine to run Windows executables automatically on Linux
    echo ':DOSWin:M::MZ::/usr/bin/wine:' > /proc/sys/fs/binfmt_misc/register
