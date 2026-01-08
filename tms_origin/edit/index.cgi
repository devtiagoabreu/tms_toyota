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

my $str_DATA_EDIT_MENU		= &TMSstr::get_str( "DATA_EDIT_MENU"		);
my $str_SHIFT_DATA		= &TMSstr::get_str( "SHIFT_DATA"		);
my $str_OPERATOR_DATA		= &TMSstr::get_str( "OPERATOR_DATA"		);
my $str_SHOW_STYLE_LIST		= &TMSstr::get_str( "SHOW_STYLE_LIST"		);
my $str_SET_STYLE		= &TMSstr::get_str( "SET_STYLE"			);
my $str_CHANGE_LOOM_NAME	= &TMSstr::get_str( "CHANGE_LOOM_NAME"		);
my $str_DELETE_DATA		= &TMSstr::get_str( "DELETE_DATA"		);
my $str_REPORT_DATA_RESTRUCTION	= &TMSstr::get_str( "REPORT_DATA_RESTRUCTION"	);
my $str_STOP_HISTORY		= &TMSstr::get_str( "STOP_HISTORY"		);

my $submit_disable = "";
if( &TMSdeny::is_demo_mode() == 1){ $submit_disable = " disabled"; }
elsif( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $tbl_width = 630;
my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

my $menu_width = 250;
my $colspan = 2;

my $title = $str_DATA_EDIT_MENU;
my $cgifile = 'apply.cgi';
my $submit_button = $str_REPORT_DATA_RESTRUCTION;

print	"<html lang=$lang>\n".
	"<head>\n".
	"<STYLE TYPE=\"text/css\">\n".
	"A:link    { color: Midnightblue }\n".
	"A:visited { color: Midnightblue }\n".
	"A:active  { color: Red }\n".
	"</STYLE>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  var submit_disflg = 0;\n".
	"  function disable_submit() {\n".
	"    document.fminput.submit.disabled = true;\n".
	"    if(submit_disflg==0){\n".
	"      submit_disflg = 1;\n".
	"      return true;\n".
	"    }else{\n".
	"      return false;\n".
	"    }\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang).

	"<BR>\n".
	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return disable_submit()\">\n".
	"<table width=$tbl_width><tr align=center><td><font size=+2><B>$title</B></font></td></tr></table>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+1 color=white>$str_SHIFT_DATA</font></th>\n".
	"<th><font size=+1 color=white>$str_OPERATOR_DATA</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color>\n".
	"<td><BR>\n".
	"<table width=$menu_width align=right cellpadding=5>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=showstyle.cgi?&data=shift><B>$str_SHOW_STYLE_LIST (Excel)</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=setstyle.cgi?data=shift><B>$str_SET_STYLE</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=select.cgi?mode=rename&data=shift><B>$str_CHANGE_LOOM_NAME</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=select.cgi?mode=delete&data=shift><B>$str_DELETE_DATA</B></A></td></tr>\n".
	"</table>\n".
	"</td>\n".

	"<td><BR>\n".
	"<table width=$menu_width align=right cellpadding=5>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=showstyle.cgi?&data=operator><B>$str_SHOW_STYLE_LIST (Excel)</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=setstyle.cgi?data=operator><B>$str_SET_STYLE</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=select.cgi?mode=rename&data=operator><B>$str_CHANGE_LOOM_NAME</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=select.cgi?mode=delete&data=operator><B>$str_DELETE_DATA</B></A></td></tr>\n".
	"</table>\n".
	"</td>\n".
	"</tr>\n".

	"<tr><th colspan=$colspan bgcolor=$menu_color><font size=+1 color=white>$str_STOP_HISTORY</font></th></tr>\n".
	"<tr><td colspan=$colspan align=center bgcolor=$body_color>\n".

	#"<table width=$menu_width align=right cellpadding=5>\n".
	"<table align=center cellpadding=5>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=hist_rename.cgi><B>$str_CHANGE_LOOM_NAME</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"../image/m.gif\" width=20 height=20 align=middle><A href=hist_delete.cgi><B>$str_DELETE_DATA</B></A></td></tr>\n".
	"</table>\n".

	"</td></tr>\n".

	"<tr><td colspan=$colspan align=center bgcolor=$body_color>\n".
	"<BR>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\"$submit_disable>\n".
	"<BR><BR>\n".
	"</td></tr>\n".

	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
