from instalar.client.console import main

# For others
def main_cli():
    exit(main())

# For windows. On Windows, scripts packaged this way need a terminal,
# so if you launch them from within a graphical application, they will make a terminal pop up.
# To prevent this from happening, use the [project.gui-scripts] table instead of [project.scripts].
# https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#creating-executable-scripts
# def main_gui():
#     main()

if __name__ == '__main__':
    main_cli()