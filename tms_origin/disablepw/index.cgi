#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSdeny;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_DISABLE_PASSWORD_FORCIBLY			= &TMSstr::get_str( "DISABLE_PASSWORD_FORCIBLY"			);
my $str_ARE_YOU_SURE_YOU_WANT_TO_DISABLE_PASSWORD	= &TMSstr::get_str( "ARE_YOU_SURE_YOU_WANT_TO_DISABLE_PASSWORD"	);
my $str_BACK						= &TMSstr::get_str( "BACK"					);
my $str_OK						= &TMSstr::get_str( "OK"					);

if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $title = $str_DISABLE_PASSWORD_FORCIBLY;

my $tbl_width = 630;
my $menu_color = "#ED1C24";
my $body_color = "#FDE1D4";

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR><BR>\n";

print	"<font size=+2><B>$str_ARE_YOU_SURE_YOU_WANT_TO_DISABLE_PASSWORD</B></font>\n";

print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=disable.cgi><IMG SRC=\"../image/ok_$lang.jpg\" width=85 height=27 alt=\"$str_OK\" border=0></A>\n".
	"<A HREF=\"javascript:history.back()\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"<NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

