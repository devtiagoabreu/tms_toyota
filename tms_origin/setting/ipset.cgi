#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSipset;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_IP_ADDRESS_SETTING			= &TMSstr::get_str( "IP_ADDRESS_SETTING"			);
my $str_RESET_MODEIFY				= &TMSstr::get_str( "RESET_MODEIFY"				);
my $str_ENTER					= &TMSstr::get_str( "ENTER"					);
my $str_IP_NUMBER_MUST_BE_BETWEEN_0_AND_255	= &TMSstr::get_str( "IP_NUMBER_MUST_BE_BETWEEN_0_AND_255"	);
my $str_PLEASE_INPUT_NUMBER			= &TMSstr::get_str( "PLEASE_INPUT_NUMBER"			);
my $str_DELETE					= &TMSstr::get_str( "DELETE"					);
my $str_RANGE_OF_IP_ADDRESS			= &TMSstr::get_str( "RANGE_OF_IP_ADDRESS"			);

my $str_LOOM_IP_ADDRESS  		= &TMSstr::get_str( 'LOOM_IP_ADDRESS'			);
my $str_USE_OF_MEMORY_CARD 		= &TMSstr::get_str( 'USE_OF_MEMORY_CARD' 		);
my $str_SCANNER_IP_ADDRESS 		= &TMSstr::get_str( 'SCANNER_IP_ADDRESS' 		);
my $str_IP_ADDRESS         		= &TMSstr::get_str( 'IP_ADDRESS'         		);
my $str_COLLECT_DATA_USING_MEMORY_CARD	= &TMSstr::get_str( 'COLLECT_DATA_USING_MEMORY_CARD'	);

my @ip_list = &TMSipset::get_ip_set_list();
my $total = ($#ip_list +3);

# スキャナー設定を読み出し
my $scan1_ip = &TMSscanner::get_scan1_ip_set();

my $tbl_width = 630;

my $title = $str_IP_ADDRESS_SETTING;
my $cgifile = 'ipset2.cgi';
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
	#"    document.fminput.elements[offset].checked = false;\n".
	"  }\n\n".

	"  function ip_check() {\n".
	"    for ( i=0; i<=$total; i++ ){\n".
	"      for ( j=((i*6)+1); j<=((i*6)+5); j++ ){\n".
	"        if( isNaN(document.fminput.elements[j].value) ){\n".
	"          window.alert(\"$str_PLEASE_INPUT_NUMBER\");\n".
	"          document.fminput.elements[j].focus();\n".
	"          document.fminput.elements[j].select();\n".
	"          return false;\n".
	"        }\n".
	"        if( parseInt(document.fminput.elements[j].value,10) > 255 ){\n".
	"          window.alert(\"$str_IP_NUMBER_MUST_BE_BETWEEN_0_AND_255\");\n".
	"          document.fminput.elements[j].focus();\n".
	"          document.fminput.elements[j].select();\n".
	"          return false;\n".
	"        }\n".
	"      }\n".
	"    }\n".
	"\n".
	"    for ( j=".((($total+1)*6)+2)."; j<=".((($total+1)*6)+5)."; j++ ){\n".
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

#### 機台のIPアドレス ####
print	"<tr bgcolor=$menu_color><th><font size=+2 color=white>$str_LOOM_IP_ADDRESS</font></th></tr>\n".
	"<tr valign=top align=center bgcolor=$body_color><td>\n".
	"<table>\n".
	"<tr align=center>\n".
	#"<th><font size=+1>$str_DELETE</font></th>\n".
	"<th></th>\n".
	"<th colspan=3><font size=+1>$str_RANGE_OF_IP_ADDRESS</font></th>\n".
	"</tr>\n";

my $offset = 0;
for( my $i=0; $i<=$#ip_list; $i++ ){
  my @data = split(/ /,$ip_list[$i]);
  print	"<tr align=center>\n".
	#"<td><input type=CHECKBOX name=\"delete$i\" OnClick=\"delete_ip($offset,6)\"></td>\n".
	"<td><input type=button name=\"del\" value=\"$str_DELETE\" OnClick=\"delete_ip($offset,5)\">&nbsp;</td>\n".
	"<td><nobr>\n".
	"<input type=text name=\"ip$i\" size=3 maxlength=3 value=\"$data[0]\"><B>.</B>\n".
	"<input type=text name=\"ip$i\" size=3 maxlength=3 value=\"$data[1]\"><B>.</B>\n".
	"<input type=text name=\"ip$i\" size=3 maxlength=3 value=\"$data[2]\"><B>.</B>\n".
	"<input type=text name=\"ip$i\" size=3 maxlength=3 value=\"$data[3]\">\n".
	"</td></nobr><td>&nbsp;&gt;&gt;&gt;&nbsp;</td><td>\n".
	"<input type=text name=\"ip$i\" size=4 maxlength=3 value=\"$data[4]\"></td></tr>\n";
  $offset += 6;
}

for( my $i=($#ip_list+1); $i<=$total; $i++ ){
  print	"<tr align=center>\n".
	#"<td><input type=CHECKBOX name=\"delete$i\" OnClick=\"delete_ip($offset,6)\"></td>\n".
	"<td><input type=button name=\"del\" value=\"$str_DELETE\" OnClick=\"delete_ip($offset,5)\">&nbsp;</td>\n".
	"<td><nobr>\n".
	"<input type=text name=\"ip$i\" size=3 maxlength=3><B>.</B>\n".
	"<input type=text name=\"ip$i\" size=3 maxlength=3><B>.</B>\n".
	"<input type=text name=\"ip$i\" size=3 maxlength=3><B>.</B>\n".
	"<input type=text name=\"ip$i\" size=3 maxlength=3>\n".
	"</td></nobr><td>&nbsp;&gt;&gt;&gt;&nbsp;</td><td>\n".
	"<input type=text name=\"ip$i\" size=4 maxlength=3></td></tr>\n";
  $offset += 6;
}
print	"</table>\n".
	"</td></tr>\n";

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

++$offset;

#### スキャナーのIPアドレス ####
print	"<tr bgcolor=$menu_color><th><font size=+2 color=white>$str_SCANNER_IP_ADDRESS</font></th></tr>\n".
	"<tr valign=top align=center bgcolor=$body_color><td>\n".

	"<table>\n".
	"<tr align=center>\n".
	#"<th><font size=+1>$str_DELETE</font></th>\n".
	"<th></th>\n".
	"<th><font size=+1>$str_IP_ADDRESS</font></th>\n".
	"</tr>\n";

my @data = split(/\./,$scan1_ip);
print	"<tr align=center>\n".
	#"<td><input type=CHECKBOX name=\"delete_scan\" OnClick=\"delete_ip($offset,5)\"></td>\n".
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
	"<input type=hidden name=\"total\" value=\"$total\">\n".
	"<input type=RESET name=\"reset\" value=\"$reset_button\">\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
