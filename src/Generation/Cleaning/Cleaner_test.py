import unittest
from src.Generation.Cleaning import Cleaner


class TestCleaner(unittest.TestCase):

    def setUp(self):

        def rr(string):
            return Cleaner.remove_repeats(Cleaner.remove_whitespace(string), 'TEST')

        self.rr = rr
        pass

    def test_simple_strings(self):
        def quick_test(test_str, correct='A|B|C|D|]'):
            self.assertEqual(correct, self.rr(test_str), test_str + ' unsuccessfully converted to ' + correct)

        basic1 = 'A|B|C|D||'
        basic2 = 'A|||B|||C|||D|||'
        basic3 = '|A|B|C|D|'
        basic4 = '|A|B|]C|D|'
        basic5 = '[|A|B|C|D|'
        basic6 = 'C:Alejandro|A|B|C|D|'
        basic7 = 'K:Dmaj|A|B|C|D|'

        quick_test(basic1)
        quick_test(basic2)
        quick_test(basic3)
        quick_test(basic4)
        quick_test(basic5)
        quick_test(basic6)
        quick_test(basic7, 'K:Dmaj|A|B|C|D|]')

    def test_simple_repeats(self):
        def quick_test(test_str, correct='A|A|B|B|C|C|D|D|]'):
            self.assertEqual(correct, self.rr(test_str), test_str + ' unsuccessfully converted to ' + correct)

        basic1 = '|:A|:B|:C|:D||'
        basic2 = 'A:|B:|C:|D:|'
        basic3 = '|A::B::C::D|'
        basic4 = '|:A::B::C::D:|'
        basic5 = '|:A:||:B:||:C:||:D:|'
        basic6 = '|:A:|:B:|:C:|:D:|'
        basic7 = '|:A|:B:|C:|D:|'

        quick_test(basic1)
        quick_test(basic2)
        quick_test(basic3)
        quick_test(basic4)
        quick_test(basic5)
        quick_test(basic6)
        quick_test(basic7)

    def test_simple_dual_repeats(self):
        def quick_test(test_str, correct='A|B|C|E|A|B|C|F|]'):
            self.assertEqual(correct, self.rr(test_str), test_str + ' unsuccessfully converted to ' + correct)

        basic1 = 'A|B|C|1E:|2F||'
        basic2 = 'A|B|C|1E:||2F||'
        basic3 = 'A|B|C|1E:|2F|]'
        basic4 = 'A|B|C|1E:|2F]|'
        basic5 = 'A|B|C|1E:|2F|'
        basic6 = 'A|B|C|1E|2F||'
        basic7 = 'A|B|C||1E:|2F||'
        basic8 = '[|A|B|C|1E:|2F||'

        quick_test(basic1)
        quick_test(basic2)
        quick_test(basic3)
        quick_test(basic4)
        quick_test(basic5)
        quick_test(basic6)
        quick_test(basic7)
        quick_test(basic8)

    def test_complex_repeats(self):
        def quick_test(test_str, correct='AB|CD|AB|CD|EF|EF|]'):
            self.assertEqual(correct, self.rr(test_str), test_str + ' unsuccessfully converted to ' + correct)

        basic1 = 'AB|CD:||:EF:|'
        basic2 = '|:AB|CD::EF:|'
        basic3 = 'AB|CD:||:EF'

        quick_test(basic1)
        quick_test(basic2)
        quick_test(basic3)

        correct2 = 'A|BCB|BCB|DF|GA|ABC|ABC|DE|DE|]'
        comp1 = 'A|:BCB:|DF|GA|:ABC|:DE|'
        comp2 = 'A|:BCB:|DF|GA|:ABC::DE|'
        comp3 = 'A|:BCB:|DF|GA|:ABC::DE:|'

        quick_test(comp1, correct2)
        quick_test(comp2, correct2)
        quick_test(comp3, correct2)

    def test_complex_dual_repeats(self):
        def quick_test(test_str, correct='A|CB|DD|CB|EE|FG|BA|CD|FG|DC|BA|]'):
            self.assertEqual(correct, self.rr(test_str), test_str + ' unsuccessfully converted to ' + correct)

        comp1 = "A|:CB|1DD:|2EE|||:FG|[1BA|CD:|[2DC|BA||"
        comp2 = "A|:CB|1DD:|2EE|:FG|[1BA|CD:|[2DC|BA||"
        comp3 = "A|:CB|1DD:|2EE||FG|[1BA|CD:|[2DC|BA||"
        comp4 = "A|:CB|1DD:|2EE||FG|[1BA|CD|[2DC|BA||"
        comp5 = "A|:CB|1DD:|2EE||FG|[1BA|CD:||2DC|BA||"

        quick_test(comp1)
        quick_test(comp2)
        quick_test(comp3)
        quick_test(comp4)
        quick_test(comp5)

    def test_current_issue(self):
        def quick_test(test_str, correct='A|CB|DD|CB|EE|FG|BA|CD|FG|DC|BA|]'):
            self.assertEqual(correct, self.rr(test_str), test_str + ' unsuccessfully converted to ' + correct)

        comp6 = "A|:CB|1DD:|2EE|FG|[1BA|CD:||2DC|BA||"
        quick_test(comp6)



