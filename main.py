import os
import re
import datetime


class OrgTodoParser():
    todoRegExpr = r'^\*\sTODO(?P<text>([a-zA-Z0-9\-]*\s){1,})(?P<tags>(\:[\w\-]*){0,})?'
    initRegExpr = r'^\*\sTODO\s.*'
    dateRegExpr = r'^SCHEDULED:\s<(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)\s(?P<dom>\w*)'
    def __init__(self):
        pass

    def parseTodo(self):
        file_directory = '/Users/terrydrymonacos/Orgzly/'
        #file_directory = '/Users/terrydrymonacos/org-test/'
        init_expr = re.compile(self.initRegExpr)
        todo_expr = re.compile(self.todoRegExpr, re.MULTILINE)

        fileList = list(filter(lambda x: x.endswith('.org'), os.listdir(file_directory)))
        self.grab_todo(fileList, file_directory, init_expr, todo_expr)

    def grab_todo(self, fileList, file_directory, init_expr, todo_expr):
        todo_list_toprint = list()
        for elem in fileList:
            with open(file_directory + elem, 'r') as fh:
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
                                    todo_message = theMatch.groupdict()['text']
                                if group_num == 3:
                                    our_tags = theMatch.groupdict()['tags']
                            if len(our_tags):

                                print("file: {} TODO text : {} TODO tags: {}".format(elem,
                                                                                     todo_message,
                                                                                     our_tags))
                            else:
                                print("file: {} TODO text : {}".format(elem.rstrip('/n'),
                                                                       todo_message))
                            todo_list_toprint.append(dict({'todo_message': todo_message,
                                                           'tags': our_tags
                                                           }
                                                          )
                                                     )
                    if found:
                        self.grab_date(k, lines, todo_list_toprint)
                    found = False
                fh.close()
                # Print out our result array
                for elem in todo_list_toprint:
                    print(elem)

    def grab_date(self, k, lines, list_of_todos):
        # let's see if the next record has our Scheduled Date
        date_expr = re.compile(self.dateRegExpr, re.MULTILINE)
        if k < len(lines):
            date_line = re.search(date_expr, lines[k+1])
            if date_line:
                # print("time: {}".format(lines[k + 1].rstrip('\n')))
                #self.print_the_stuff(date_line)
                # transform into date
                thisDate = datetime.date(int(date_line.groupdict()["year"]),
                                         int(date_line.groupdict()["month"]),
                                         int(date_line.groupdict()["day"])
                                         )
                now = datetime.date.today()
                timeDelta = thisDate - now
                if timeDelta.days <= 0:
                    if len(list_of_todos) > 1:
                        self.print_the_stuff(date_line)
                        list_of_todos[:-1].pop()

    def print_the_stuff(self, date_line):
        print("year: {} Month: {}  Day: {} fullDate: {}".format(date_line.groupdict()["year"],
                                                                date_line.groupdict()["month"],
                                                                date_line.groupdict()["day"],
                                                                date_line.groupdict()["dom"]
                                                                )
              )


def main():
    a = OrgTodoParser()
    a.parseTodo()


if __name__ == "__main__":
    main()

