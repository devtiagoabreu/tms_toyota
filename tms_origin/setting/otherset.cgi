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

my $str_OTHER_SETTING				= &TMSstr::get_str( "OTHER_SETTING"				);
my $str_RESET_MODEIFY				= &TMSstr::get_str( "RESET_MODEIFY"				);
my $str_ENTER					= &TMSstr::get_str( "ENTER"					);
my $str_IP_NUMBER_MUST_BE_BETWEEN_0_AND_255	= &TMSstr::get_str( "IP_NUMBER_MUST_BE_BETWEEN_0_AND_255"	);
my $str_PLEASE_INPUT_NUMBER			= &TMSstr::get_str( "PLEASE_INPUT_NUMBER"			);
my $str_DELETE					= &TMSstr::get_str( "DELETE"					);

my $str_USE_OF_MEMORY_CARD 		= &TMSstr::get_str( 'USE_OF_MEMORY_CARD' 		);
my $str_SCANNER_IP_ADDRESS 		= &TMSstr::get_str( 'SCANNER_IP_ADDRESS' 		);
my $str_IP_ADDRESS         		= &TMSstr::get_str( 'IP_ADDRESS'         		);
my $str_COLLECT_DATA_USING_MEMORY_CARD	= &TMSstr::get_str( 'COLLECT_DATA_USING_MEMORY_CARD'	);


# スキャナー設定を読み出し
my $scan1_ip = &TMSscanner::get_scan1_ip_set();

my $tbl_width = 630;

my $title = $str_OTHER_SETTING;
my $cgifile = 'otherset2.cgi';
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';
my $reset_button  = $str_RESET_MODEIFY;
my $submit_button = $str_ENTER;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function delete_ip(offset,num) {\n".
	"    for ( i=(offset+1); i<=(offset+num); i++ ){\n".
	"      document.fminput.elements[i].value = \"\";\n".
	"    }\n".
	"  }\n\n".

	"  function ip_check() {\n".
	"    for ( j=1+1; j<=1+4; j++ ){\n".
	"      if( isNaN(document.fminput.elements[j].value) ){\n".
	"        window.alert(\"$str_PLEASE_INPUT_NUMBER\");\n".
	"        document.fminput.elements[j].focus();\n".
	"        document.fminput.elements[j].select();\n".
	"        return false;\n".
	"      }\n".
	"      if( parseInt(document.fminput.elements[j].value,10) > 255 ){\n".
	"        window.alert(\"$str_IP_NUMBER_MUST_BE_BETWEEN_0_AND_255\");\n".
	"        document.fminput.elements[j].focus();\n".
	"        document.fminput.elements[j].select();\n".
	"        return false;\n".
	"      }\n".
	"    }\n".
	"    return true;\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n";

print	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return ip_check()\">\n".

	"<table width=$tbl_width><tr><th><font size=+2>$title</font></th></tr></table>\n".
	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n";

#### JAT710のメモリーカード ####
print	"<tr bgcolor=$menu_color><th><font size=+2 color=white>$str_USE_OF_MEMORY_CARD</font></th></tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<br>\n";

my $checked = "";
if( -f "..\\..\\tmsdata\\setting\\memcard.txt" ){ $checked = "checked"; }

print	"<input type=CHECKBOX name=\"use_memcard\" value=\"yes\" $checked>\n".
	$str_COLLECT_DATA_USING_MEMORY_CARD."\n".
	"<br><br>\n".
	"</td></tr>\n";

#### スキャナーのIPアドレス ####
print	"<tr bgcolor=$menu_color><th><font size=+2 color=white>$str_SCANNER_IP_ADDRESS</font></th></tr>\n".
	"<tr valign=top align=center bgcolor=$body_color><td>\n".

	"<table>\n".
	"<tr align=center>\n".
	"<th></th>\n".
	"<th><font size=+1>$str_IP_ADDRESS</font></th>\n".
	"</tr>\n";

my $offset = 1;
my @data = split(/\./,$scan1_ip);
print	"<tr align=center>\n".
	"<td><input type=button name=\"del_scan\" value=\"$str_DELETE\" OnClick=\"delete_ip($offset,4)\">&nbsp;</td>\n".
	"<td><nobr>\n".
	"<input type=text name=\"scan1_ip\" size=3 maxlength=3 value=\"$data[0]\"><B>.</B>\n".
	"<input type=text name=\"scan1_ip\" size=3 maxlength=3 value=\"$data[1]\"><B>.</B>\n".
	"<input type=text name=\"scan1_ip\" size=3 maxlength=3 value=\"$data[2]\"><B>.</B>\n".
	"<input type=text name=\"scan1_ip\" size=3 maxlength=3 value=\"$data[3]\">\n".
	"</td></tr>\n";

print	"</table>\n".
	"<br>\n".

	"</td></tr>\n";

#### submit ボタン ####
print	"<tr><td align=center bgcolor=$body_color>\n".
	"<input type=RESET name=\"reset\" value=\"$reset_button\">\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
