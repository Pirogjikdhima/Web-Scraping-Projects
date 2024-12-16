import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GlobeDataCollection import (
    find_next_link,
    save,
    submain,
    get_telefonia,
    get_foto_dhe_video,
    get_elektroshtepiake_te_medha,
    get_elektroshtepiake_te_vogla,
    get_kompjutera_dhe_rrjeti,
    get_kondicionimi
)

class TestGlobeDataCollection(unittest.TestCase):

    def test_find_next_link(self):
        html_content = '''
        <div class="ty-pagination__items">
            <span>1</span>
            <a class="cm-history ty-pagination__item cm-ajax" href="page2.html">2</a>
        </div>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        next_link = find_next_link(soup)
        self.assertEqual(next_link, "page2.html")

        html_content_no_next = '''
        <div class="ty-pagination__items">
            <span>2</span>
        </div>
        '''
        soup = BeautifulSoup(html_content_no_next, 'html.parser')
        next_link = find_next_link(soup)
        self.assertFalse(next_link)

    @patch('GlobeDataCollection.requests.get')
    def test_save(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body>Mock HTML content</body></html>'
        mock_get.return_value = mock_response

        test_filename = 'test.csv'
        expected_path = os.path.join("Globe", test_filename).replace("\\", "/")

        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            next_link = save(mock_response, test_filename)
            self.assertFalse(next_link)
            mock_file.assert_called_once_with(
                expected_path, 'w', newline='', encoding='utf-8', errors='strict'
            )

    @patch('GlobeDataCollection.save')
    @patch('GlobeDataCollection.requests.get')
    def test_submain(self, mock_get, mock_save):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        mock_save.return_value = False

        submain('telefonia', filename='test.csv')
        mock_get.assert_called_once_with('https://globe.al/telefonia/')
        mock_save.assert_called_once_with(mock_response, filename='test.csv')

    @patch('GlobeDataCollection.submain')
    def test_category_functions(self, mock_submain):
        get_telefonia()
        mock_submain.assert_called_with('telefonia', filename='GlobeTelefonia.csv')

        get_foto_dhe_video()
        mock_submain.assert_called_with('foto-video-sq', filename='GlobeFotoDheVideo.csv')

        get_elektroshtepiake_te_medha()
        mock_submain.assert_called_with('elektroshtepiake-te-medha-sq', filename='GlobeElektroshtepiakeTeMedha2.csv')

        get_elektroshtepiake_te_vogla()
        mock_submain.assert_called_with('elektroshtepiake-te-vogla-sq', filename='GlobeElektroshtepiakeTeVogla.csv')

        get_kompjutera_dhe_rrjeti()
        mock_submain.assert_called_with('kompjutera-dhe-rrjeti', filename='GlobeKompjuteraDheRrjeti.csv')

        get_kondicionimi()
        mock_submain.assert_called_with('kondicionimi', filename='GlobeKondicionimi.csv')

if __name__ == '__main__':
    unittest.main()
