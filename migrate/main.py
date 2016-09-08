import argparse
import glob
import os
import parser


LICENSE = ('# This Source Code Form is subject to the terms of the '
           'Mozilla Public\n# License, v. 2.0. If a copy of the MPL '
           'was not distributed with this\n# file, You can obtain '
           'one at http://mozilla.org/MPL/2.0/.\n')


DTD_PARSER = parser.getParser('.dtd')


def get_translation_from_dtd(path, name):
    DTD_PARSER.readFile(path)
    entities, map = DTD_PARSER.parse()
    entity = entities[map[name]]
    return entity.val.encode('utf-8')


def create_properties_file(path):
    print 'creating new *.properties file: %s' % path
    prop_file = open(path, 'w+')
    prop_file.write(LICENSE)
    prop_file.close()


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
        dtd_file, dtd_name = before.split(':')
        prop_file, prop_name = after.split(':')

        dtd_path = os.path.join(l10n_path, dtd_file)
        if not os.path.isfile(dtd_path):
            print 'dtd path: [%s] is invalid' % dtd_path
            continue
        translation = get_translation_from_dtd(dtd_path, dtd_name)

        prop_path = os.path.join(l10n_path, prop_file)
        if not os.path.isfile(prop_path):
            create_properties_file(prop_path)

        with open(prop_path, 'a') as prop_file:
            prop_file.write('\n# LOCALIZATION NOTE (' + prop_name + ')\n')
            prop_file.write(prop_name + '=' + translation + '\n')


def main():
    # Read arguments
    arg_parser = argparse.ArgumentParser(
            description='Migrate devtools localized strings.')
    arg_parser.add_argument('path', type=str, help='path to l10n repository')
    arg_parser.add_argument('-c', '--config', type=str,
                            help='path to configuration file or folder')
    args = arg_parser.parse_args()

    # Retrieve path to devtools localization files in l10n repository.
    devtools_l10n_path = os.path.join(args.path, 'devtools/client/')
    if not os.path.exists(devtools_l10n_path):
        print 'l10n path: [%s] is invalid' % devtools_l10n_path
        exit()
    print 'l10n path: [%s] is valid' % devtools_l10n_path

    if os.path.isdir(args.config):
        conf_files = glob.glob(args.config + '*')
    elif os.path.isfile(args.config):
        conf_files = [args.config]
    else:
        print 'config path: [%s] is invalid' % args.config
        exit()

    for conf_file in conf_files:
        print 'performing migration for [%s]' % conf_file
        migrate_conf(conf_file, devtools_l10n_path)


if __name__ == '__main__':
    main()
