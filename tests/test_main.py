from datetime import date
import os
import unittest
from unittest.mock import MagicMock, Mock, patch

from src.main import (
    get_html,
    parse_html,
    render_response,
    send_mail,
    main,
)

class TestGetHtml(unittest.TestCase):
    URL = 'https://example.com'

    @patch('src.main.urlopen')
    def test_get_html_return_html_200(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.code = 200
        mock_resp.read.return_value = b'<html>OK</html>'

        mock_urlopen.return_value = mock_resp

        html = get_html(TestGetHtml.URL)

        self.assertEqual(html, '<html>OK</html>')

    @patch('src.main.urlopen')
    def test_get_html_raises_error_404(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.code = 404
        mock_resp.read.return_value = b'Not Found'
        mock_urlopen.return_value = mock_resp

        with self.assertRaises(Exception):
            get_html(TestGetHtml.URL)

    @patch('src.main.urlopen')
    def test_get_html_raises_error_500(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.code = 500
        mock_resp.read.return_value = b'Server Error'
        mock_urlopen.return_value = mock_resp

        with self.assertRaises(Exception):
            get_html(TestGetHtml.URL)

class TestParseHtml(unittest.TestCase):
    def test_parse_html_single_valid_href(self):
        html = """
        <!-- List Items -->
        <a href="https://store.steampowered.com/app/4391750/Halcyon_Days_at_Taoyuan__Galloping_Horse_Pack/?snr=1_7_7_2300_150_1">Game</a>
        <!-- End List Items -->
        """
        result = parse_html(html)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Halcyon Days at Taoyuan  Galloping Horse Pack')
        self.assertEqual(result[0]['link'], 'https://store.steampowered.com/app/4391750/Halcyon_Days_at_Taoyuan__Galloping_Horse_Pack/?snr=1_7_7_2300_150_1')

    def test_parse_html_multiple_valid_hrefs(self):
        html = """
        <!-- List Items -->
        <a href="https://store.steampowered.com/app/123/Game_One/?snr=1_2_3">One</a>
        <a href="https://store.steampowered.com/app/456/Game_Two/?snr=4_5_6">Two</a>
        <!-- End List Items -->
        """
        result = parse_html(html)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Game One')
        self.assertEqual(result[1]['name'], 'Game Two')

    def test_parse_html_multiple_comments(self):
        html = """
        <!-- List Items -->
        <a href="https://store.steampowered.com/app/123/Game_One/?snr=1_2_3">One</a>
        <a href="https://store.steampowered.com/app/456/Game_Two/?snr=4_5_6">Two</a>
        <!-- End List Items -->
        <!-- List Items -->
        <a href="https://store.steampowered.com/app/123/Game_Three/?snr=7_2_3">Three</a>
        <a href="https://store.steampowered.com/app/456/Game_Four/?snr=9_5_6">Four</a>
        <!-- End List Items -->
        """
        result = parse_html(html)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0]['name'], 'Game One')
        self.assertEqual(result[1]['name'], 'Game Two')
        self.assertEqual(result[2]['name'], 'Game Three')
        self.assertEqual(result[3]['name'], 'Game Four')

    def test_parse_html_no_list_items_comment(self):
        html = """
        <a href="https://store.steampowered.com/app/123/Game_One/?snr=1_2_3">One</a>
        """
        result = parse_html(html)
        self.assertEqual(result, [])

    def test_parse_html_start_comment_only(self):
        html = "<!-- List Items -->"
        result = parse_html(html)
        self.assertEqual(result, [])

    def test_parse_html_list_items_without_end_comment(self):
        html = """
        <!-- List Items -->
        <a href="https://store.steampowered.com/app/123/Game_One/?snr=1_2_3">One</a>
        <a href="https://store.steampowered.com/app/456/Game_Two/?snr=4_5_6">Two</a>
        """
        result = parse_html(html)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Game One')
        self.assertEqual(result[1]['name'], 'Game Two')

    def test_parse_html_end_comment_only(self):
        html = "<!-- End List Items -->"
        result = parse_html(html)
        self.assertEqual(result, [])

    def test_parse_html_list_items_without_start_comment(self):
        html = """
        <a href="https://store.steampowered.com/app/123/Game_One/?snr=1_2_3">One</a>
        <a href="https://store.steampowered.com/app/456/Game_Two/?snr=4_5_6">Two</a>
        <!-- End List Items -->
        """
        result = parse_html(html)
        self.assertEqual(result, [])

    def test_parse_html_invalid_href_pattern_raises(self):
        html = """
        <!-- List Items -->
        <a href="https://store.steampowered.com/app/123/INVALID-HREF/?snr=1_2_3">Bad</a>
        <!-- End List Items -->
        """
        with self.assertRaises(Exception):
            parse_html(html)

    def test_parse_html_href_without_snr_raises(self):
        html = """
        <!-- List Items -->
        <a href="https://store.steampowered.com/app/123/Game_Without_SNR/">Missing SNR</a>
        <!-- End List Items -->
        """
        with self.assertRaises(Exception):
            parse_html(html)

    def test_parse_html_nested_tags_inside_a(self):
        html = """
        <!-- List Items -->
        <a href="https://store.steampowered.com/app/789/Nested_Tag/?snr=7_8_9"><span>Nested</span></a>
        <!-- End List Items -->
        """
        result = parse_html(html)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Nested Tag')
    
    def test_parse_html_trailing_slash_in_href(self):
        html = """
        <!-- List Items -->
        <a href="https://store.steampowered.com/app/101112/Trailing_Slash/?snr=1_1_1/">Game</a>
        <!-- End List Items -->
        """
        result = parse_html(html)
        self.assertEqual(result[0]['name'], 'Trailing Slash')

class TestRenderResponse(unittest.TestCase):
    TODAY = date.today()

    @patch('src.main.date')
    def test_render_response_empty_list(self, mock_date):
        mock_date.today.return_value = TestRenderResponse.TODAY
        data = []
        result = render_response(data)
        expected_result = (f"Ahoj, dne {TestRenderResponse.TODAY} jsem navštívil Steam a našel tyto hry se 100% slevou!\n" 
        + "Žádné hry se 100% slevou nebyly nalezeny. :-(")
        self.assertEqual(result, expected_result)
    
    @patch('src.main.date')
    def test_render_response_single_game(self, mock_date):
        mock_date.today.return_value = TestRenderResponse.TODAY
        data = [{'name': 'Game One', 'link': 'https://example.com/game1'}]
        result = render_response(data)
        expected = (
            f"Ahoj, dne {TestRenderResponse.TODAY} jsem navštívil Steam a našel tyto hry se 100% slevou!\n"
            "Jméno: Game One\n"
            "Link: https://example.com/game1\n"
            "****\n"
        )
        self.assertEqual(result, expected)

    @patch('src.main.date')
    def test_render_response_multiple_games(self, mock_date):
        mock_date.today.return_value = TestRenderResponse.TODAY
        data = [
            {'name': 'Game One', 'link': 'https://example.com/game1'},
            {'name': 'Game Two', 'link': 'https://example.com/game2'}
        ]
        result = render_response(data)
        expected = (
            f"Ahoj, dne {TestRenderResponse.TODAY} jsem navštívil Steam a našel tyto hry se 100% slevou!\n"
            "Jméno: Game One\n"
            "Link: https://example.com/game1\n"
            "****\n"
            "Jméno: Game Two\n"
            "Link: https://example.com/game2\n"
            "****\n"
        )
        self.assertEqual(result, expected)

    @patch('src.main.date')
    def test_render_response_special_characters(self, mock_date):
        mock_date.today.return_value = TestRenderResponse.TODAY
        data = [{'name': 'Gáme_Špeciál', 'link': 'https://example.com/špeciál'}]
        result = render_response(data)
        expected = (
            f"Ahoj, dne {TestRenderResponse.TODAY} jsem navštívil Steam a našel tyto hry se 100% slevou!\n"
            "Jméno: Gáme_Špeciál\n"
            "Link: https://example.com/špeciál\n"
            "****\n"
        )
        self.assertEqual(result, expected)

class TestSendMail(unittest.TestCase):
    @patch('src.main.SMTP_SSL')
    def test_send_mail_success(self, mock_smtp_ssl):
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server
        
        mock_server.send_message.return_value = {'recipient@example.com': (250, 'OK')}

        msg = "Test message"
        config = {
            'host': 'smtp.example.com',
            'port': 465,
            'email': 'me@example.com',
            'password': 'secret',
            'recipients': ['recipient@example.com']
        }

        result = send_mail(msg, config)

        self.assertEqual(result, {'recipient@example.com': (250, 'OK')})

        mock_server.login.assert_called_once_with(user='me@example.com', password='secret')
        mock_server.send_message.assert_called_once_with(
            msg=msg,
            from_addr='me@example.com',
            to_addrs=['recipient@example.com']
        )

    @patch('src.main.SMTP_SSL')
    def test_send_mail_login_raises(self, mock_smtp_ssl):
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server
        mock_server.login.side_effect = Exception("Login failed")

        msg = "Test"
        config = {
            'host': 'smtp.example.com',
            'port': 465,
            'email': 'me@example.com',
            'password': 'wrong',
            'recipients': ['a@b.com']
        }

        with self.assertRaises(Exception) as context:
            send_mail(msg, config)
        self.assertIn("Login failed", str(context.exception))

    @patch('src.main.SMTP_SSL')
    def test_send_mail_send_message_raises(self, mock_smtp_ssl):
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server
        mock_server.send_message.side_effect = Exception("Send failed")

        msg = "Test"
        config = {
            'host': 'smtp.example.com',
            'port': 465,
            'email': 'me@example.com',
            'password': 'secret',
            'recipients': ['a@b.com']
        }

        with self.assertRaises(Exception) as context:
            send_mail(msg, config)
        self.assertIn("Send failed", str(context.exception))

class TestMain(unittest.TestCase):
    @patch('src.main.send_mail')
    @patch('src.main.render_response')
    @patch('src.main.parse_html')
    @patch('src.main.get_html')
    @patch.dict(os.environ, {
        'RECIPIENTS': 'a@b.com,b@c.com',
        'SERVER': 'smtp.example.com',
        'PORT': '465',
        'EMAIL': 'me@example.com',
        'PASSWORD': 'secret'
    })
    def test_main_pipeline_success(self, mock_get_html, mock_parse_html, mock_render, mock_send):
        mock_get_html.return_value = '<html>fake</html>'
        mock_parse_html.return_value = [{'name':'Game','link':'https://example.com'}]
        mock_render.return_value = 'REPORT'
        mock_send.return_value = {'a@b.com': (250, 'OK'), 'b@c.com': (250, 'OK')}

        result = main()

        mock_get_html.assert_called_once_with('https://store.steampowered.com/search?maxprice=free&supportedlang=english&specials=1&hidef2p=1')
        mock_parse_html.assert_called_once_with('<html>fake</html>')
        mock_render.assert_called_once_with([{'name':'Game','link':'https://example.com'}])
        mock_send.assert_called_once_with('REPORT', {
            'host': 'smtp.example.com',
            'port': '465',
            'email': 'me@example.com',
            'password': 'secret',
            'recipients': ['a@b.com','b@c.com']
        })

        self.assertEqual(result, {'a@b.com': (250, 'OK'), 'b@c.com': (250, 'OK')})

    @patch.dict(os.environ, {
        'RECIPIENTS': '', 
        'SERVER': '',
        'PORT': '',
        'EMAIL': '',
        'PASSWORD': ''
    })
    def test_main_incomplete_smtp_config_raises(self):
        with self.assertRaises(Exception) as context:
            main()
        self.assertIn("SMTP connection can't be established", str(context.exception))