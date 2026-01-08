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

my $str_LANGUAGE_SETTING	= &TMSstr::get_str( "LANGUAGE_SETTING"	);
my $str_RESET_MODEIFY		= &TMSstr::get_str( "RESET_MODEIFY"	);
my $str_ENTER			= &TMSstr::get_str( "ENTER"		);

my $tbl_width = 630;

my $title = $str_LANGUAGE_SETTING;
my $cgifile = 'langset2.cgi';
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';
my $reset_button  = $str_RESET_MODEIFY;
my $submit_button = $str_ENTER;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n".

	"<form name=\"fminput\" action=\"$cgifile\" method=POST>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".

	"<tr valign=top align=center bgcolor=$body_color><td>\n".
	"<table>\n";

my $lang_set  = &TMSstr::get_lang_set();
my @lang_list = &TMSstr::get_lang_list();
my @lang_name = &TMSstr::get_lang_name();

for( my $i=0; $i<=$#lang_list; $i++ ){
  print	"<tr><td align=left><input type=radio name=\"lang\" value=\"$lang_list[$i]\"";
  if( $lang_set eq $lang_list[$i] ){ print " checked"; }
  print	"><B>$lang_name[$i]</B></td></tr>\n";
}

print	"</table>\n".
	"</td></tr>\n";


my $checked_jat = "";
my $checked_lwt = "";
if( &TMSselitem::is_jat_ari() ){ $checked_jat = "checked"; }
if( &TMSselitem::is_lwt_ari() ){ $checked_lwt = "checked"; }

print	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>Loom Type</font></th>\n".
	"</tr>\n".
	"<tr valign=top align=center bgcolor=$body_color><td>\n".
	"<table>\n".
	"<tr><td><input type=checkbox name=\"jat\" value=\"ari\" $checked_jat> <B>JAT</B> ( Air Jet Loom )</td></tr>\n".
	"<tr><td><input type=checkbox name=\"lwt\" value=\"ari\" $checked_lwt> <B>LWT</B> ( Water Jet Loom )</td></tr>\n".
	"</table>\n".
	"</td></tr>\n".

	"<tr><td align=center bgcolor=$body_color>\n".
	"<input type=RESET name=\"reset\" value=\"$reset_button\">\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

