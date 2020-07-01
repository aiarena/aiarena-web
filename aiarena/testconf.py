import types
from unittest.result import failfast
from django.test import TestCase as TC
from django.test import SimpleTestCase as STC, TransactionTestCase as TTC
import colorama
from colorama import init as color_init
from colorama import Fore, Back, Style
color_init()


@failfast
def addFailureSansTraceback(self, test, err):
    err_sans_tb = (err[0], err[1], None)
    self.errors.append((test, self._exc_info_to_string(err_sans_tb, test)))
    self._mirrorOutput = True


class TestCase(TC):
    def run(self, result=None):
        if result and len(result.errors):
            result.addError = types.MethodType(addFailureSansTraceback, result)
        if result and len(result.failures):
            result.addFailure = types.MethodType(addFailureSansTraceback, result)
        super(TestCase, self).run(result)
        if len(result.failures):
            res = Back.RED + f" {result}"
        else:
            res = Fore.GREEN + f" {result}"
        print(Fore.BLUE + str(self) + " " + str(res) + Style.RESET_ALL)

class SimpleTestCase(TestCase, STC):
    pass

class TransactionTestCase(TestCase,TTC):
    pass
