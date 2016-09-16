import argparse
import glob
import logging
import os
import parser
import urllib2

# Configure logging format and level
logging.basicConfig(format='  [%(levelname)s] %(message)s', level=logging.INFO)

# License header to use when creating new properties files.
LICENSE = ('# This Source Code Form is subject to the terms of the '
           'Mozilla Public\n# License, v. 2.0. If a copy of the MPL '
           'was not distributed with this\n# file, You can obtain '
           'one at http://mozilla.org/MPL/2.0/.\n')


# Base url to retrieve properties files on central, that will be parsed for
# localization notes.
CENTRAL_BASE_URL = ('https://hg.mozilla.org/'
                    'mozilla-central/raw-file/tip/'
                    'devtools/client/locales/en-US/')


# Use this url to test migrations on strings that did not land yet.
DEV_BASE_URL = ('https://hg.mozilla.org/'
                'try/raw-file/eec2fac3231f12ea16689a7c7aec057032551a50/'
                'devtools/client/locales/en-US/')


# Cache to store properties files retrieved over the network.
central_properties = {}


# Retrieve the current version of the provided properties file filename from
# devtools/client on mozilla central.
def get_central_prop_file(prop_filename):
    if prop_filename in central_properties:
        return central_properties[prop_filename]

    url = DEV_BASE_URL + prop_filename
    logging.info('loading localization notes from central: {%s}' % url)

    try:
        central_properties[prop_filename] = urllib2.urlopen(url).readlines()
    except:
        logging.error('failed to load properties file on central : {%s}' % url)
        central_properties[prop_filename] = []

    return central_properties[prop_filename]


# Retrieve the current en-US localization notes for the provided prop_name.
def get_localization_note(prop_name, prop_filename):
    prop_file = get_central_prop_file(prop_filename)
    comment_buffer = []
    for i, line in enumerate(prop_file):
        # Remove line breaks.
        line = line.strip('\n').strip('\r')

        if line.startswith('#'):
            # Comment line, add to the current comment buffer.
            comment_buffer.append(line)
        elif line.startswith(prop_name + '='):
            # Property found, the current comment buffer is the localization
            # note.
            return '\n'.join(comment_buffer)
        else:
            # No match, not a comment, reinitialize the comment buffer.
            comment_buffer = []

    logging.warning('localization notes could not be found for: {%s}'
                    % prop_name)
    return '# LOCALIZATION NOTE (%s)\n' % prop_name


# Extract the value of an entity in a dtd file.
def get_translation_from_dtd(dtd_path, entity_name):
    dtd_parser = parser.getParser('.dtd')
    dtd_parser.readFile(dtd_path)
    entities, map = dtd_parser.parse()
    entity = entities[map[entity_name]]
    return entity.val.encode('utf-8')


# Create a new properties file at the provided path.
def create_properties_file(path):
    logging.info('creating new *.properties file: {%s}' % path)
    prop_file = open(path, 'w+')
    prop_file.write(LICENSE)
    prop_file.close()


# Migrate a single string entry for a dtd to a properties file.
def migrate_string(dtd_path, prop_path, dtd_name, prop_name):
    if not os.path.isfile(dtd_path):
        logging.error('dtd path is invalid: {%s}' % dtd_path)
        return

    translation = get_translation_from_dtd(dtd_path, dtd_name)

    # Create properties file if missing.
    if not os.path.isfile(prop_path):
        create_properties_file(prop_path)

    prop_filename = os.path.basename(prop_path)
    prop_line = prop_name + '=' + translation + '\n'

    # Skip the string if it already exists in the destination file.
    prop_file_content = open(prop_path, 'r').read()
    if prop_line in prop_file_content:
        logging.warning('string already migrated, skipping: {%s}' % prop_name)
        return
    # Skip the string and log an error if an existing entry is found, but with
    # a different value.
    if ('\n' + prop_name + '=') in prop_file_content:
        logging.error('existing string found, skipping: {%s}' % prop_name)
        return

    logging.info('migrating {%s} in {%s}' % (prop_name, prop_filename))
    with open(prop_path, 'a') as prop_file:
        localization_note = get_localization_note(prop_name, prop_filename)
        prop_file.write('\n' + localization_note)
        prop_file.write('\n' + prop_line)


# Apply the migration instructions in the provided configuration file.
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

        # Expected syntax: ${prop_path}:${prop_name} = ${dtd_path}:${dtd_name}.
        prop_info, dtd_info = line.split(' = ')
        prop_path, prop_name = prop_info.split(':')
        dtd_path, dtd_name = dtd_info.split(':')

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
        logging.error('l10n path is invalid: {%s}' % devtools_l10n_path)
        exit()
    logging.info('l10n path is valid: {%s}' % devtools_l10n_path)

    # Retrieve configuration files to apply.
    if os.path.isdir(args.config):
        conf_files = glob.glob(args.config + '*')
    elif os.path.isfile(args.config):
        conf_files = [args.config]
    else:
        logging.error('config path is invalid: {%s}' % args.config)
        exit()

    # Perform migration for each configuration file.
    for conf_file in conf_files:
        logging.info('performing migration for config file: {%s}' % conf_file)
        migrate_conf(conf_file, devtools_l10n_path)


if __name__ == '__main__':
    main()
