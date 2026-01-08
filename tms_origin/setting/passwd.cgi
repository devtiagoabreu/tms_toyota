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

my $str_PASSWORD_SETTING		= &TMSstr::get_str( "PASSWORD_SETTING"			);
my $str_RESET_MODEIFY			= &TMSstr::get_str( "RESET_MODEIFY"			);
my $str_ENTER				= &TMSstr::get_str( "ENTER"				);
my $str_PASSWORD_IS_TOO_SHORT		= &TMSstr::get_str( "PASSWORD_IS_TOO_SHORT"		);
my $str_NEED_6_CHARACTERS_OR_MORE	= &TMSstr::get_str( "NEED_6_CHARACTERS_OR_MORE"		);
my $str_CANT_USE_SPACE_FOR_PASSWORD	= &TMSstr::get_str( "CANT_USE_SPACE_FOR_PASSWORD"	);
my $str_THE_PASSWORDS_DO_NOT_MATCH	= &TMSstr::get_str( "THE_PASSWORDS_DO_NOT_MATCH"	);
my $str_DISABLE_PASSWORD		= &TMSstr::get_str( "DISABLE_PASSWORD"			);
my $str_ENABLE_PASSWORD			= &TMSstr::get_str( "ENABLE_PASSWORD"			);
my $str_USERNAME			= &TMSstr::get_str( "USERNAME"				);
my $str_NEW_PASSWORD			= &TMSstr::get_str( "NEW_PASSWORD"			);
my $str_CONFIRM_NEW_PASSWORD		= &TMSstr::get_str( "CONFIRM_NEW_PASSWORD"		);
my $str_PASSWORD_TARGET_AREA		= &TMSstr::get_str( "PASSWORD_TARGET_AREA"		);
my $str_LOOM_DATA			= &TMSstr::get_str( "LOOM_DATA"				);
my $str_SETTING				= &TMSstr::get_str( "SETTING"				);
my $str_DATA_EDIT			= &TMSstr::get_str( "DATA_EDIT"				);

my $submit_disable = "";
if( &TMSdeny::is_demo_mode() == 1){ $submit_disable = " disabled"; }
elsif( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $disable_passwd = '';
my $enable_passwd  = '';
if( -f ".htaccess" ){ $enable_passwd  = ' checked'; }
else{                 $disable_passwd = ' checked'; }

my $tbl_width = 630;
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';

my $title = $str_PASSWORD_SETTING;
my $cgifile = 'passwd2.cgi';
my $reset_button  = $str_RESET_MODEIFY;
my $submit_button = $str_ENTER;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".

	"<script language=JavaScript>\n".
	"<!--\n".
	"  function passwdchk() {\n".
	"    if( document.fminput.passwd_on[1].checked == true ){\n".
	"      var passwd1 = document.fminput.passwd1.value;\n".
	"      var passwd2 = document.fminput.passwd2.value;\n".
	"      if( passwd1.length < 6 ){\n".
	"        window.alert(\"$str_PASSWORD_IS_TOO_SHORT ($str_NEED_6_CHARACTERS_OR_MORE)\");\n".
	"        document.fminput.passwd1.focus();\n".
	"        document.fminput.passwd1.select();\n".
	"        return false;\n".
	"      }\n".
	"      for( i=0; i<passwd1.length; i++ ){\n".
	"        if( passwd1.charAt(i) == \" \" ){\n".
	"          window.alert(\"$str_CANT_USE_SPACE_FOR_PASSWORD\");\n".
	"          document.fminput.passwd1.focus();\n".
	"          document.fminput.passwd1.select();\n".
	"          return false;\n".
	"        }\n".
	"      }\n".
	"      if( passwd1 != passwd2 ){\n".
	"        window.alert(\"$str_THE_PASSWORDS_DO_NOT_MATCH\");\n".
	"        document.fminput.passwd2.focus();\n".
	"        document.fminput.passwd2.select();\n".
	"        return false;\n".
	"      }\n".
	"    }\n".
	"    return true;\n".
	"  }\n".
	"//-->\n".
	"</script>\n".

	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n".

	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return passwdchk()\">\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color><th><font size=+2 color=white>$title</font></th></tr>\n".
	"<tr valign=top align=center bgcolor=$body_color><td>\n";

print	"<BR>\n".
	"<B>$str_PASSWORD_TARGET_AREA</B><BR>\n".
	"<font color=blue><B>".
	"&lt;&nbsp;$str_LOOM_DATA&nbsp;&gt;&nbsp;&nbsp;".
	"&lt;&nbsp;$str_SETTING&nbsp;&gt;&nbsp;&nbsp;".
	"&lt;&nbsp;$str_DATA_EDIT&nbsp;&gt;".
	"</B></font><BR><BR>\n".
	"<table align=center>\n".
	"<tr><td></td><td><input type=radio name=\"passwd_on\" value=\"0\"$disable_passwd><B>$str_DISABLE_PASSWORD</B></td></tr>\n".
	"<tr><td></td><td><input type=radio name=\"passwd_on\" value=\"1\"$enable_passwd><B>$str_ENABLE_PASSWORD</B></td></tr>\n".
	"</table>\n".
	"<BR>\n".
	"<table align=center>\n".
	"<tr><td align=right><B>$str_USERNAME:</B></td><td>&nbsp;<font size=+1><B>TMS</B></font></td></tr>\n".
	"<tr><td align=right><B>$str_NEW_PASSWORD:</B></td><td><input type=password name=\"passwd1\" size=30 maxlength=30></td></tr>\n".
	"<tr><td align=right><B>$str_CONFIRM_NEW_PASSWORD:</B></td><td><input type=password name=\"passwd2\" size=30 maxlength=30></td></tr>\n".
	"</table>\n".
	"<BR>\n";

print	"</td></tr>\n".
	"<tr><td align=center bgcolor=$body_color>\n".
	"<input type=RESET name=\"reset\" value=\"$reset_button\">\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\"$submit_disable>\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

