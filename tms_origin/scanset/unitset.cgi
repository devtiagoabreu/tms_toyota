#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_UNIT_SETTING	= &TMSstr::get_str( 'UNIT_SETTING'	);
my $str_UPDATE_SETTING	= &TMSstr::get_str( 'UPDATE_SETTING'	);
my $str_UPDATE_OK	= &TMSstr::get_str( 'UPDATE_OK'		);
my $str_SCANNER		= &TMSstr::get_str( 'SCANNER'		);
my $str_LENGTH_UNIT	= &TMSstr::get_str( 'LENGTH_UNIT'	);
my $str_DENSITY_UNIT	= &TMSstr::get_str( 'DENSITY_UNIT'	);

################################################################

my $length_unit;
my $beam_unit;  ## dummy
my $density_unit;

## 設定ファイル読み出し
&TMSscanner::get_unit_setting( \$length_unit, \$beam_unit, \$density_unit );

################################################################

my $tbl_width = 630;

my $title = $str_UNIT_SETTING;
my $cgifile = 'unitset2.cgi';
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';
my $submit_button = $str_UPDATE_SETTING;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function checkSubmit(aForm) {\n".
	"    return confirm(\"$str_UPDATE_OK\");\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n";

print	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return checkSubmit(this);\">\n".
	"<table width=$tbl_width><tr><th><font size=+2>$title</font></th></tr></table>\n";

print	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$str_LENGTH_UNIT</font></th>\n".
	"<th><font size=+2 color=white>$str_DENSITY_UNIT</font></th></tr>\n".

	"<tr valign=top align=center bgcolor=$body_color><td>\n".
	"<br>\n".
	"<TABLE>\n";

my @str_LENGTH_UNIT = &TMSscanner::get_str_length_unit_name();

my @checked = ("","","");
$checked[$length_unit] = "checked";

print	"<TR><TD><input type=radio name=\"length_unit\" value=\"0\" $checked[0]>$str_LENGTH_UNIT[0]</TD></TR>\n".
	"<TR><TD><input type=radio name=\"length_unit\" value=\"1\" $checked[1]>$str_LENGTH_UNIT[1]</TD></TR>\n".
	"<TR><TD><input type=radio name=\"length_unit\" value=\"2\" $checked[2]>$str_LENGTH_UNIT[2]</TD></TR>\n".
 	"</TABLE>\n".
	"<br>\n".
	"</TD>\n".

	"<TD>\n".
	"<br>\n".
	"<TABLE>\n";

my @str_DENSITY_UNIT = &TMSscanner::get_str_density_unit_name();

@checked = ("","");
$checked[$density_unit] = "checked";

print	"<TR><TD><input type=radio name=\"density_unit\" value=\"0\" $checked[0]>$str_DENSITY_UNIT[0]</TD></TR>\n".
	"<TR><TD><input type=radio name=\"density_unit\" value=\"1\" $checked[1]>$str_DENSITY_UNIT[1]</TD></TR>\n".
	"</TABLE>\n".
	"<br>\n".

	"</td></tr>\n";

#### submit ボタン ####
print	"<tr><td align=center bgcolor=$body_color colspan=2>\n".

	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
