#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSselitem;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_REPORT_SETTING		= &TMSstr::get_str( "REPORT_SETTING"		);
my $str_PLEASE_CHECK_COLOR_NUM	= &TMSstr::get_str( "PLEASE_CHECK_COLOR_NUM"	);
my $str_PLEASE_INPUT_NUMBER	= &TMSstr::get_str( "PLEASE_INPUT_NUMBER"	);
my $str_BEAM_TYPE		= &TMSstr::get_str( "BEAM_TYPE"			);
my $str_REPORT_ITEM		= &TMSstr::get_str( "REPORT_ITEM"		);
my $str_STOP_CAUSE		= &TMSstr::get_str( "STOP_CAUSE"		);
my $str_DETAIL_OF_STOP_CAUSE	= &TMSstr::get_str( "DETAIL_OF_STOP_CAUSE"	);
my $str_UNIT			= &TMSstr::get_str( "UNIT"			);
my $str_PERIOD			= &TMSstr::get_str( "PERIOD"			);
my $str_START_OF_WEEK		= &TMSstr::get_str( "START_OF_WEEK"		);
my $str_OTHER_SETTING		= &TMSstr::get_str( "OTHER_SETTING"		);
my $str_CONDITION_OF_TOTALING	= &TMSstr::get_str( "CONDITION_OF_TOTALING"	);
my $str_EFFICIENCY		= &TMSstr::get_str( "EFFICIENCY"		);
my $str_RUN_TIME		= &TMSstr::get_str( "RUN_TIME"			);
my $str_PERCENT_OVER		= &TMSstr::get_str( "PERCENT_OVER"		);
my $str_MINUITE_OVER		= &TMSstr::get_str( "MINUITE_OVER"		);
my $str_RESET_MODEIFY		= &TMSstr::get_str( "RESET_MODEIFY"		);
my $str_ENTER			= &TMSstr::get_str( "ENTER"			);

my @menu_item2  = &TMSselitem::get_menu_of_item2();
my @menu_item   = &TMSselitem::get_menu_of_item();
my @menu_item3  = &TMSselitem::get_menu_of_item3();
my @menu_detail = &TMSselitem::get_menu_of_detail();
my @menu_color  = &TMSselitem::get_menu_of_color();
my @menu_bmtype = &TMSselitem::get_menu_of_beam_type();
my @menu_unit   = &TMSselitem::get_menu_of_unit();
my @menu_period = &TMSselitem::get_menu_of_period();
my @menu_week   = &TMSselitem::get_menu_of_week();

my @key_item2  = &TMSselitem::get_key_of_item2();
my @key_item   = &TMSselitem::get_key_of_item();
my @key_item3  = &TMSselitem::get_key_of_item3();
my @key_detail = &TMSselitem::get_key_of_detail();
my @key_color  = &TMSselitem::get_key_of_color();
my @key_bmtype = &TMSselitem::get_key_of_beam_type();
my @key_unit   = &TMSselitem::get_key_of_unit();
my @key_period = &TMSselitem::get_key_of_period();
my @key_week   = &TMSselitem::get_key_of_week();

my @val_item2  = &TMSselitem::get_value_of_item2();
my @val_item   = &TMSselitem::get_value_of_item();
my @val_item3  = &TMSselitem::get_value_of_item3();
my @val_detail = &TMSselitem::get_value_of_detail();
my @val_color  = &TMSselitem::get_value_of_color();
my $val_bmtype = &TMSselitem::get_value_of_beam_type();
my $val_unit   = &TMSselitem::get_value_of_unit();
my $val_period = &TMSselitem::get_value_of_period();
my $val_week   = &TMSselitem::get_value_of_week();
my $val_effic  = &TMSselitem::get_value_of_effic();
my $val_run_tm = &TMSselitem::get_value_of_run_tm();
my $val_expire = &TMSselitem::get_value_of_expire();

my $jat_ari = &TMSselitem::is_jat_ari();
my $lwt_ari = &TMSselitem::is_lwt_ari();

my $tbl_width = 630;
if( $lang eq 'pt' ){ $tbl_width = 700; }

my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';

my $title = $str_REPORT_SETTING;
my $cgifile = 'selitem2.cgi';
my $reset_button = $str_RESET_MODEIFY;
my $submit_button = $str_ENTER;

my $color_max = "6";  # for JavaScript
if( $jat_ari == 0 ){ $color_max = "3"; }

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function check_beam_type() {\n".
	"    val = document.fminput.beam_type[0].checked;\n".
	"    document.fminput.item2[0].disabled = val;\n".
	"    document.fminput.item[0].disabled = val;\n".
	"  }\n".
	"  function check_weft_detail() {\n".
	"    val = false;\n".
	"    if( (document.fminput.detail[0].checked == false)\n".
	"      && (document.fminput.detail[1].checked == false)\n".
	"      && (document.fminput.detail[2].checked == false) ){\n".
	"      val = true;\n".
	"    }\n".
	"    for( i=0; i<$color_max; i++ ){\n".
	"      document.fminput.color[i].disabled = val;\n".
	"    }\n".
	"  }\n".
	"  function initialize() {\n".
	"    check_beam_type();\n".
	"    check_weft_detail();\n".
	"  }\n".
	"  function delay_init() {\n".
	"    setTimeout(\"initialize()\",10);\n".  # 10msec後（Reset完了後に initialize() したい）
	"  }\n".
	"  function check_input() {\n".
	"    if( (document.fminput.detail[0].checked == true)\n".
	"      || (document.fminput.detail[1].checked == true)\n".
	"      || (document.fminput.detail[2].checked == true) ){\n".
	"      val = false\n".
	"      for( i=0; i<6; i++ ){\n".
	"        if( document.fminput.color[i].checked == true ){ val = true; break; }\n".
	"      }\n".
	"      if( val == false ){\n".
	"        window.alert(\"$str_PLEASE_CHECK_COLOR_NUM\");\n".
	"        document.fminput.color[0].focus();\n".
	"        return false;\n".
	"      }\n".
	"    }\n".
	"    if( isNaN(document.fminput.effic.value) ){\n".
	"      window.alert(\"$str_PLEASE_INPUT_NUMBER\");\n".
	"      document.fminput.effic.focus();\n".
	"      document.fminput.effic.select();\n".
	"      return false;\n".
	"    }\n".
	"    if( isNaN(document.fminput.effic.value) ){\n".
	"      window.alert(\"$str_PLEASE_INPUT_NUMBER\");\n".
	"      document.fminput.effic.focus();\n".
	"      document.fminput.effic.select();\n".
	"      return false;\n".
	"    }\n".
	"    if( isNaN(document.fminput.run_tm.value) ){\n".
	"      window.alert(\"$str_PLEASE_INPUT_NUMBER\");\n".
	"      document.fminput.run_tm.focus();\n".
	"      document.fminput.run_tm.select();\n".
	"      return false;\n".
	"    }\n".
	"    if( isNaN(document.fminput.expire.value) ){\n".
	"      window.alert(\"$str_PLEASE_INPUT_NUMBER\");\n".
	"      document.fminput.expire.focus();\n".
	"      document.fminput.expire.select();\n".
	"      return false;\n".
	"    }\n".
	"    return true;\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2 onLoad=\"initialize()\"><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n".

	"<form name=\"fminput\" action=\"$cgifile\" method=POST onReset=\"delay_init()\" onSubmit=\"return check_input()\">\n".
	"<table width=$tbl_width><tr align=center><td><font size=+2><B>$title</B></font></td></tr></table>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th width=30%><font size=+1 color=white>$str_REPORT_ITEM</font></th>\n".
	"<th width=30%><font size=+1 color=white>$str_STOP_CAUSE</font></th>\n".
	"<th><font size=+1 color=white>$str_BEAM_TYPE</font></th>\n".
	"</tr>\n".

	"<tr valign=top align=right bgcolor=$body_color>\n".
	"<td rowspan=3>\n".
	"<table align=center>\n";

for(my $i=0; $i<=$#key_item2; $i++){
  print "<tr><td align=left><input type=checkbox name=\"item2\" value=\"$key_item2[$i]\"";
  if( $val_item2[$i] ){ print " checked"; }
  print ">$menu_item2[$i]</td></tr>\n";
}

print	"</table>\n".
	"</td><td rowspan=3>\n".
	"<table align=center>\n";

my @item_line = ();
for(my $i=0; $i<=$#key_item; $i++){
  my $line = "<tr><td align=left><input type=checkbox name=\"item\" value=\"$key_item[$i]\"";
  if( $val_item[$i] ){ $line .= " checked"; }
  $line .= ">$menu_item[$i]</td></tr>\n";
  $item_line[$i] = $line;
}
my @item3_line = ();
for(my $i=0; $i<=$#key_item; $i++){
  my $line = "<tr><td align=left><input type=checkbox name=\"item3\" value=\"$key_item3[$i]\"";
  if( ($i<=1) and ($lwt_ari == 0) ){ # CC前、CC後
    $line .= " disabled><font color=gray>$menu_item3[$i]</font>";
  }else{
    if( $val_item3[$i] ){ $line .= " checked"; }
    $line .= ">$menu_item3[$i]";
  }
  $item3_line[$i] = $line."</td></tr>\n";;
}

# 並び替えて表示
print $item_line[0];   # 経ミス(上)
print $item_line[1];   # 経ミス
print $item_line[5];   # 緯ミス
print $item_line[2];   # 捨て耳
print $item3_line[2];  # もじり
print "<tr><td><hr></td></tr>\n";
print $item_line[6];   # 機揚がり
print $item_line[7];   # 切り卸し
print $item_line[8];   # 手動停止
print $item_line[9];   # 電源OFF
print $item_line[10];  # その他

print	"</table>\n".
	"</td><td>\n".
	"<table align=center>\n";

for( my $i=0; $i<=$#key_bmtype; $i++ ){
  print	"<tr><td align=left><input type=radio name=\"beam_type\" value=\"$key_bmtype[$i]\"";
  if( $val_bmtype == $key_bmtype[$i] ){ print " checked"; }
  print	" onClick=\"check_beam_type()\">$menu_bmtype[$i]</td></tr>\n";
}

print	"</table>\n".
	"</td></tr>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+1 color=white>$str_DETAIL_OF_STOP_CAUSE</font></th></tr>\n".
	"<tr valign=top align=center bgcolor=$body_color><td>\n".
	"<table>\n";

print	"<tr><td valign=top>\n".
	"<table align=center>\n";

# WF1、WF2、LH
for( my $i=0; $i<=$#key_detail; $i++ ){
  print	"<tr><td align=left><input type=checkbox name=\"detail\" value=\"$key_detail[$i]\"";
  if( $val_detail[$i] ){ print " checked"; }
  print " onClick=\"check_weft_detail()\">$menu_detail[$i]";
  print "</td></tr>\n";
}
print $item3_line[0];  # 捨て耳(前)
print $item3_line[1];  # 捨て耳(後)
print $item_line[3];   # もじり(右)
print $item_line[4];   # もじり(左)

print	"</table>\n".
	"</td><td valign=top>\n".
	"<table align=center>\n";

# カラー１～６
for( my $i=0; $i<=$#key_color; $i++ ){
  print	"<tr><td align=left><input type=checkbox name=\"color\" value=\"$key_color[$i]\"";
  if( ($i>=3) and ($jat_ari == 0) ){
    print " disabled><font color=gray>$menu_color[$i]</font>";
  }else{
    if( $val_color[$i] ){ print " checked"; }
    print ">$menu_color[$i]";
  }
  print "</td></tr>\n";
}
print	"</table>\n".
	"</td></tr>\n";

print	"</table>\n".
	"</td></tr>\n".
	"</table>\n";

###########################################################################################
# 二段目

print	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th width=20%><font size=+1 color=white>$str_UNIT</font></th>\n".
	"<th width=20%><font size=+1 color=white>$str_PERIOD</font></th>\n".
	"<th width=20%><font size=+1 color=white>$str_START_OF_WEEK</font></th>\n".
	"<th><font size=+1 color=white>$str_OTHER_SETTING</font></th>\n".
	"</tr>\n".

	"<tr valign=top align=right bgcolor=$body_color><td>\n".
	"<table align=center>\n";

for( my $i=0; $i<=$#key_unit; $i++ ){
  print	"<tr><td align=left><input type=radio name=\"unit\" value=\"$key_unit[$i]\"";
  if( $val_unit == $key_unit[$i] ){ print " checked"; }
  print	">$menu_unit[$i]</td></tr>\n";
}

print	"</table>\n".
	"</td><td>\n".
	"<table align=center>\n";

for( my $i=0; $i<=$#key_period; $i++ ){
  print	"<tr><td align=left><input type=radio name=\"period\" value=\"$key_period[$i]\"";
  if( $val_period eq $key_period[$i] ){ print " checked"; }
  print	">$menu_period[$i]</td></tr>\n";
}

print	"</table>\n".
	"</td><td>\n".
	"<table align=center>\n";

for( my $i=0; $i<=$#key_week; $i++ ){
  print	"<tr><td align=left><input type=radio name=\"week\" value=\"$key_week[$i]\"";
  if( $val_week == $key_week[$i] ){ print " checked"; }
  print	">$menu_week[$i]</td></tr>\n";
}

print	"</table>\n".
	"</td><td align=center>\n".
	"<table align=center>\n".
	"<tr><td colspan=2 align=center>$str_CONDITION_OF_TOTALING</td></tr>\n".
	"<tr><td>$str_EFFICIENCY</td><td nowrap><input type=text name=\"effic\" size=5 maxlength=5 value=\"$val_effic\">$str_PERCENT_OVER</td></tr>\n".
	"<tr><td>$str_RUN_TIME</td><td nowrap><input type=text name=\"run_tm\" size=5 maxlength=6 value=\"$val_run_tm\">$str_MINUITE_OVER</td></tr>\n".
	"</table>\n".
	"<br>\n".
	&TMSstr::get_str("DATA_COLLECTION_WARNING_TIME")."<br>\n".
	"<input type=text name=\"expire\" size=5 maxlength=5 value=\"$val_expire\">".&TMSstr::get_str("HOUR")."\n".
	"</td></tr>\n".

	"<tr><td colspan=4 align=center bgcolor=$body_color>\n".
	"<input type=RESET name=\"reset\" value=\"$reset_button\">\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

