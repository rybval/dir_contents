import sys
sys.path.append(r'H:\dir_contents\lib')
import tree
books = tree.Root(r'E:\Книги')
books = tree.Root(r'E:\Книги')
if not books.getContent(lambda it: not it.isAccessible(), deep=True):
    print('FAIL')
else:
    print('PASS')
