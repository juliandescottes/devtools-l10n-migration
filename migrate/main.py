import argparse
import glob
import os
import parser


# License header to use when creating new properties files.
LICENSE = ('# This Source Code Form is subject to the terms of the '
           'Mozilla Public\n# License, v. 2.0. If a copy of the MPL '
           'was not distributed with this\n# file, You can obtain '
           'one at http://mozilla.org/MPL/2.0/.\n')


# Extract the value of an entity in a dtd file.
def get_translation_from_dtd(dtd_path, entity_name):
    dtd_parser = parser.getParser('.dtd')
    dtd_parser.readFile(dtd_path)
    entities, map = dtd_parser.parse()
    entity = entities[map[entity_name]]
    return entity.val.encode('utf-8')


# Create a new properties file at the provided path.
def create_properties_file(path):
    print '[INFO] creating new *.properties file: %s' % path
    prop_file = open(path, 'w+')
    prop_file.write(LICENSE)
    prop_file.close()


# Migrate a single string entry for a dtd to a properties file.
def migrate_string(dtd_path, prop_path, dtd_name, prop_name):
    if not os.path.isfile(dtd_path):
        print '[ERROR] dtd path is invalid: %s' % dtd_path
        return
    translation = get_translation_from_dtd(dtd_path, dtd_name)

    if not os.path.isfile(prop_path):
        create_properties_file(prop_path)

    new_line = prop_name + '=' + translation + '\n'

    # Skip the string if it already exists in the destination file.
    prop_as_str = open(prop_path, 'r').read()
    if new_line in prop_as_str:
        print '[WARNING] property already migrated, skipping: %s' % prop_name
        return

    # Skip the string and log an error if an existing entry is found, but with
    # a different value
    if ('\n' + prop_name + '=') in prop_as_str:
        print '[ERROR] existing entry found, skipping: %s' % prop_name
        return

    print '[INFO] migrating %s in %s' % (prop_name, os.path.basename(prop_path))
    with open(prop_path, 'a') as prop_file:
        localization_notes = '\n# LOCALIZATION NOTE (%s)\n' % prop_name
        prop_file.write(localization_notes)
        prop_file.write(new_line)


# Apply the migration instructions in the provided configuration file
def migrate_conf(conf_path, l10n_path):
    f = open(conf_path, 'r')
    lines = f.readlines()
    f.close()

    for i, line in enumerate(lines):
        # Remove line breaks.
        line = line.strip('\n').strip('\r')

        # Skip invalid lines.
        if ' = ' not in line:
            continue

        # Expected syntax : ${dtd_path}:${dtd_name} = ${prop_path}:${prop_name}
        before, after = line.split(' = ')
        dtd_path, dtd_name = before.split(':')
        prop_path, prop_name = after.split(':')

        dtd_path = os.path.join(l10n_path, dtd_path)
        prop_path = os.path.join(l10n_path, prop_path)

        migrate_string(dtd_path, prop_path, dtd_name, prop_name)


def main():
    # Read command line arguments.
    arg_parser = argparse.ArgumentParser(
            description='Migrate devtools localized strings.')
    arg_parser.add_argument('path', type=str, help='path to l10n repository')
    arg_parser.add_argument('-c', '--config', type=str,
                            help='path to configuration file or folder')
    args = arg_parser.parse_args()

    # Retrieve path to devtools localization files in l10n repository.
    devtools_l10n_path = os.path.join(args.path, 'devtools/client/')
    if not os.path.exists(devtools_l10n_path):
        print '[ERROR] l10n path is invalid: %s' % devtools_l10n_path
        exit()
    print '[INFO] l10n path is valid: %s' % devtools_l10n_path

    # Retrieve configuration files to apply.
    if os.path.isdir(args.config):
        conf_files = glob.glob(args.config + '*')
    elif os.path.isfile(args.config):
        conf_files = [args.config]
    else:
        print '[ERROR] config path is invalid: %s' % args.config
        exit()

    # Perform migration for each configuration file.
    for conf_file in conf_files:
        print '[INFO] performing migration for [%s]' % conf_file
        migrate_conf(conf_file, devtools_l10n_path)


if __name__ == '__main__':
    main()
