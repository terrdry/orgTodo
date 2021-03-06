import os
import re
import datetime
import argparse


def create_argparser():
    """
    Create the argument parser and return the object that has access to the parameters
    :return: parser object
    """
    parser = argparse.ArgumentParser(description="Orgzly to Obsidian Markup")
    parser.add_argument("--srcdir",
                        action="store",
                        default="/Users/terrydrymonacos/Orgzly/",
                        metavar="source_directory",
                        help="Directory containing the Orgzly files")
    parser.add_argument("--postdays",
                        action="store",
                        default=0,
                        type=int,
                        metavar='post',
                        help="Select the number of days to include after today")
    parser.add_argument("--outfile",
                        action="store",
                        default="/Users/terrydrymonacos/Orgzly/today.md",
                        metavar='output',
                        help="location and name of output file")
    return parser

class OrgTodoParser():
    todoRegExpr = r'^\*\sTODO(?P<text>([a-zA-Z0-9\-]*\s){1,})(?P<tags>(\:[\w\-]*){0,})?'
    initRegExpr = r'^\*\sTODO\s.*'
    dateRegExpr = r'^SCHEDULED:\s<(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)\s(?P<dom>\w*)'

    def __init__(self, input_dir, postdays, output_file):
        self.input_dir = input_dir
        self.postdays = postdays
        self.output_file = output_file
        self.list_to_print = list()

    def prepare_parsing(self):
        init_expr = re.compile(self.initRegExpr)
        todo_expr = re.compile(self.todoRegExpr, re.MULTILINE)

        file_list = list(filter(lambda x: x.endswith('.org'), os.listdir(self.input_dir)))
        self.process_todo(file_list, self.input_dir, init_expr, todo_expr)

    def process_todo(self, file_list, file_directory, init_expr, todo_expr):
        for elem in file_list:
            with open(file_directory + elem, 'r') as fh:
                self.read_file(fh, init_expr, todo_expr)

        # process the list now and filter out the dates
        self.filter_dates()

        # Print out our result array
        self.print_to_file()

    def print_to_file(self):
        with open(self.output_file, "w") as fh:
            fh.writelines([self.to_org_format(elem) for elem in self.list_to_print])

    def read_file(self, fh, init_expr, todo_expr):
        lines = fh.readlines()
        for k, item in enumerate(lines):
            todo_match = re.search(init_expr, item)
            found = False
            if todo_match:
                found = True
                matches = re.finditer(todo_expr, item)
                our_tags = 0
                for matchNum, theMatch in enumerate(matches):
                    for group_num in range(0, len(theMatch.groups())):
                        if group_num == 1:
                            todo_message = theMatch.groupdict()['text'].strip('\n')
                        if group_num == 3:
                            our_tags = theMatch.groupdict()['tags']
                    self.list_to_print.append(dict({'todo_message': todo_message,
                                                        'tags': our_tags,
                                                        'date': ""
                                                    }
                                                   )
                                              )
            if found:
               self.grab_date(k, lines)

    def grab_date(self, k, lines):
        # let's see if the next record has our Scheduled Date
        date_expr = re.compile(self.dateRegExpr, re.MULTILINE)
        if k+1 < len(lines):
            date_line = re.search(date_expr, lines[k+1])
            if date_line:
                # transform into date
                this_date = datetime.date(int(date_line.groupdict()["year"]),
                                          int(date_line.groupdict()["month"]),
                                          int(date_line.groupdict()["day"])
                                          )
                self.list_to_print[-1]['date'] = this_date


    def filter_dates(self):
        for k in range(len(self.list_to_print) - 1, -1, -1):
            if self.list_to_print[k]['date']:
                this_date = self.list_to_print[k]['date']
                now = datetime.date.today()
                time_delta = this_date - now
                if not( time_delta.days <= self.postdays):
                    del self.list_to_print[k]
            else:
                del self.list_to_print[k]

    def to_org_format(self, date_element):
        return " - [ ] #todo {}  <span class='cm-strong'>{}</span>\n".format(date_element['todo_message'], date_element['date'])


def main(input_directory, postdays, output_file):
    a = OrgTodoParser(input_directory, postdays, output_file)
    a.prepare_parsing()


if __name__ == "__main__":
    parser = create_argparser()
    parsed_args = parser.parse_args()
    main(parsed_args.srcdir,
         parsed_args.postdays,
         parsed_args.outfile
         )

