#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSselitem;

require '../common/http_header.pm';

my $lang = "en";  # 英語固定
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"		);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"		);
my $str_NO_VALID_DATA_FOUND	= &TMSstr::get_str( "NO_VALID_DATA_FOUND"	);
my $str_MENU			= &TMSstr::get_str( "MENU"			);
my $str_BACK			= &TMSstr::get_str( "BACK"			);

my $html = new CGI;

my $newlang = $html->param('lang');
if( length($newlang) > 0 ){ &TMSstr::save_language($newlang); }

my $jat = $html->param('jat');
my $lwt = $html->param('lwt');
if( $jat ne "ari" ){ $jat = "nashi"; }
if( $lwt ne "ari" ){ $lwt = "nashi"; }
&TMSselitem::save_mac_type($jat,$lwt);

my $tbl_width = 630;
my $title = $str_SETTING_RESULT;
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR><BR>\n";

if( length($newlang) > 0 ){
  print	"<font size=+2><B>$str_SETTING_SUCCEED</B></font>\n";
} else{
  print	"<font size=+2><B>$str_NO_VALID_DATA_FOUND</B></font>\n";
}

print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"<A HREF=\"langset.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

