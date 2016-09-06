import argparse
import fileinput
import os
import re


def get_value_from_dtd(path, name):
    f = open(path, 'r')
    lines = f.readlines()
    f.close()

    for i, line in enumerate(lines):
        m = re.search('ENTITY\s+' + name + '\s+"([^"]+)"', line)
        if m and m.group(1):
            return m.group(1)


def replace_value_properties(path, name, value):
    found = False
    for line in fileinput.input(path, inplace=True):
        if re.search(name + '=(\w+)$', line):
            line = name + '=' + value
            found = True
        print line,
    fileinput.close()

    if found:
        return

    with open(path, 'a') as f:
        f.write('\n# LOCALIZATION NOTE (' + name + '): '
                'LOCALIZATION NOTE MISSING\n')
        f.write(name + '=' + value + '\n')


def main():
    parser = argparse.ArgumentParser(
            description='Migrate devtools localized strings.')
    parser.add_argument('path', type=str, help='path of your L10N clone')
    parser.add_argument('-c', '--config', type=str,
                        help='path of the configuration file',
                        default='config')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print "path: [%s] is invalid" % args.path
        exit()

    print "path: [%s] is valid" % args.path

    if not os.path.isfile(args.config):
        print "config: no file found at [%s]" % args.config
        exit()

    print "config: file found at [%s]" % args.config

    f = open(args.config, 'r')
    lines = f.readlines()
    f.close()

    for i, line in enumerate(lines):
        line = line.strip('\n')
        if ' = ' not in line:
            continue

        [before, after] = line.split(' = ')
        [dtdFile, beforeName] = before.split(':')

        dtd_path = os.path.join(args.path, 'devtools/client/', dtdFile)
        if not os.path.isfile(dtd_path):
            print 'Can not find previous dtd file'
            exit()

        # XXX get_value_dtd is undefined ?
        translation = get_value_dtd(dtd_path, beforeName)

        if ':' not in after:
            continue

        propertiesFile, afterName = after.split(':')
        properties_path = os.path.join(args.path, 'devtools/client/',
                                       propertiesFile)

        if not os.path.isfile(properties_path):
            pfile = open(properties_path, 'w+')
            pfile.close()

        replace_value_properties(properties_path, afterName, translation)


if __name__ == '__main__':
    main()
