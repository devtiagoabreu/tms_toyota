#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSdeny;

use TMSswitchdata;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SWITCH_USE_DATA		= &TMSstr::get_str( "SWITCH_USE_DATA"		);
my $str_SWITCH_DATA		= &TMSstr::get_str( "SWITCH_DATA"		);
my $str_CURRENT_USE_DATA	= &TMSstr::get_str( "CURRENT_USE_DATA"		);
my $str_NOT_EXIST		= &TMSstr::get_str( "NOT_EXIST"			);
my $str_SELECT_SWITCH_DATA	= &TMSstr::get_str( "SELECT_SWITCH_DATA"	);
my $str_EXEC_SWITCH_DATA	= &TMSstr::get_str( "EXEC_SWITCH_DATA"		);
my $str_RENAME_DATA		= &TMSstr::get_str( "RENAME_DATA"		);
my $str_NEW_NAME		= &TMSstr::get_str( "NEW_NAME"			);
my $str_SELECT_RENAME_DATA	= &TMSstr::get_str( "SELECT_RENAME_DATA"	);
my $str_EXEC_RENAME_DATA	= &TMSstr::get_str( "EXEC_RENAME_DATA"		);
my $str_CREATE_DATA		= &TMSstr::get_str( "CREATE_DATA"		);
my $str_CREATE_NAME		= &TMSstr::get_str( "CREATE_NAME"		);
my $str_EXEC_CREATE_DATA	= &TMSstr::get_str( "EXEC_CREATE_DATA"		);
my $str_DELETE_DATA		= &TMSstr::get_str( "DELETE_DATA"		);
my $str_SELECT_DELETE_DATA	= &TMSstr::get_str( "SELECT_DELETE_DATA"	);
my $str_EXEC_DELETE_DATA	= &TMSstr::get_str( "EXEC_DELETE_DATA"		);
my $str_PLEASE_SELECT_DATA	= &TMSstr::get_str( "PLEASE_SELECT_DATA"	);
my $str_PLEASE_INPUT_NAME	= &TMSstr::get_str( "PLEASE_INPUT_NAME"		);
my $str_DUPLICATE_NAME		= &TMSstr::get_str( "DUPLICATE_NAME"		);
my $str_DELETE_SELECT_DATA_OK	= &TMSstr::get_str( "DELETE_SELECT_DATA_OK"	);

my $submit_disable = "";
if( &TMSdeny::is_demo_mode() == 1){ $submit_disable = " disabled"; }
elsif( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

#----------------------------------------------------------------------------------------------------
# データ名のリスト作成

my @data_name_list = ();  # データ名のリスト

&TMSswitchdata::get_save_data_name(\@data_name_list);  # 保存データ名

my $current_name = &TMSswitchdata::get_current_data_name(\@data_name_list);  # 現在使用中のデータ名

@data_name_list = sort @data_name_list;

# ---------------------------------------------------------------------------------------------------
# ここから html 文生成

my $tbl_width = 630;
my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

my $cgifile = 'switchdata2.cgi';
my $title = $str_SWITCH_USE_DATA;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function switch_chk() {\n".
	"    if( document.fminput1.dataname.selectedIndex == -1 ){\n".
	"      window.alert(\"$str_PLEASE_SELECT_DATA\");\n".
	"      return false\n".
	"    }\n".
	"    return true;\n".
	"  }\n".
	"  function rename_chk() {\n".
	"    if( document.fminput2.dataname.selectedIndex == -1 ){\n".
	"      window.alert(\"$str_PLEASE_SELECT_DATA\");\n".
	"      return false\n".
	"    }\n".
	"    if( document.fminput2.newname.value.length == 0 ){\n".
	"      window.alert(\"$str_PLEASE_INPUT_NAME\");\n".
	"      return false\n".
	"    }\n".
	"    val = document.fminput2.newname.value.toUpperCase();\n".
	"    len = document.fminput2.dataname.length;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      if( document.fminput2.dataname[i].value.toUpperCase() == val ){\n".
	"        window.alert(\"$str_DUPLICATE_NAME\");\n".
	"        return false\n".
	"      }\n".
	"    }\n".
	"    return true;\n".
	"  }\n".
	"  function create_chk() {\n".
	"    if( document.fminput3.newname.value.length == 0 ){\n".
	"      window.alert(\"$str_PLEASE_INPUT_NAME\");\n".
	"      return false\n".
	"    }\n".
	"    val = document.fminput3.newname.value.toUpperCase();\n".
	"    len = document.fminput2.dataname.length;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      if( document.fminput2.dataname[i].value.toUpperCase() == val ){\n".
	"        window.alert(\"$str_DUPLICATE_NAME\");\n".
	"        return false\n".
	"      }\n".
	"    }\n".
	"    return true;\n".
	"  }\n".
	"  function delete_chk() {\n".
	"    if( document.fminput4.dataname.selectedIndex == -1 ){\n".
	"      window.alert(\"$str_PLEASE_SELECT_DATA\");\n".
	"      return false\n".
	"    }\n".
	"    res = window.confirm(\"$str_DELETE_SELECT_DATA_OK\");\n".
	"    if( res == false){ return false; }\n".
	"    return true;\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n".
	"<table width=$tbl_width><tr align=center><td><font size=+2><B>$title</B></font></td></tr></table>".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$str_SWITCH_DATA</font></th>\n".
	"<th><font size=+2 color=white>$str_RENAME_DATA</font></th>\n".
	"</tr>\n";

# ---- データの切り替え --------------------------------------------------

print	"<form name=\"fminput1\" action=\"$cgifile\" method=POST onSubmit=\"return switch_chk()\">\n".
	"<input type=hidden name=\"mode\" value=\"switch\">\n".
	"<td align=center valign=bottom bgcolor=$body_color width=50%>\n".
	"<font color=green><B>&lt$str_CURRENT_USE_DATA&gt</B></font><br>\n";

if( length($current_name) == 0 ){ print "<font color=red size=+1><B>$str_NOT_EXIST</B></font>\n"; }
else{	                          print "<font color=blue size=+1><B>$current_name</B></font>\n";  }

print	"<br><br>\n".
	"<font color=green><B>&lt$str_SELECT_SWITCH_DATA&gt</B></font><br>\n".
	"<select name=\"dataname\" size=10>\n";

foreach(@data_name_list){
  unless( $_ eq $current_name ){ print "<option value=\"$_\">$_</option>\n"; }
}
print	"</select><br><br>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$str_EXEC_SWITCH_DATA\">\n".
	"</td>\n".
	"</form>\n";

# ---- データ名の変更 --------------------------------------------------

print	"<form name=\"fminput2\" action=\"$cgifile\" method=POST onSubmit=\"return rename_chk()\">\n".
	"<input type=hidden name=\"mode\" value=\"rename\">\n".
	"<td align=center valign=bottom bgcolor=$body_color>\n".
	"<font color=green><B>&lt$str_SELECT_RENAME_DATA&gt</B></font><br>\n".
	"<select name=\"dataname\" size=10>\n";

foreach(@data_name_list){
  if( $_ eq $current_name ){ print "<option value=\"$_\" style=\"color=blue\">$_</option>\n"; }
  else{                      print "<option value=\"$_\">$_</option>\n"; }
}

print	"</select><br><br>\n".
	"<font color=green><B>&lt;$str_NEW_NAME&gt;</B></font><br>\n".
	"<input type=text name=\"newname\"size=25><br><br>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$str_EXEC_RENAME_DATA\"$submit_disable>\n".
	"</td>\n".
	"</form>\n";

#--------------------------------------------------------------------------------------

print	"</tr><tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$str_CREATE_DATA</font></th>\n".
	"<th><font size=+2 color=white>$str_DELETE_DATA</font></th>\n".
	"</tr><tr>\n";

# ---- データ領域の新規作成 --------------------------------------------------

print	"<form name=\"fminput3\" action=\"$cgifile\" method=POST onSubmit=\"return create_chk()\">\n".
	"<input type=hidden name=\"mode\" value=\"create\">\n".
	"<td align=center valign=bottom bgcolor=$body_color>\n".
	"<font color=green><B>&lt;$str_CREATE_NAME&gt;</B></font><br>\n".
	"<input type=text name=\"newname\"size=25><br><br>\n".
	"<br><br><br><br>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$str_EXEC_CREATE_DATA\"$submit_disable>\n".
	"</td>\n".
	"</form>\n";

# ---- データの削除 --------------------------------------------------

print	"<form name=\"fminput4\" action=\"$cgifile\" method=POST onSubmit=\"return delete_chk()\">\n".
	"<input type=hidden name=\"mode\" value=\"delete\">\n".
	"<td align=center valign=bottom bgcolor=$body_color>\n".
	"<font color=green><B>&lt$str_SELECT_DELETE_DATA&gt</B></font><br>\n".
	"<select name=\"dataname\" size=10>\n";

foreach(@data_name_list){
  if( $_ eq $current_name ){ print "<option value=\"$_\" style=\"color=blue\">$_</option>\n"; }
  else{                      print "<option value=\"$_\">$_</option>\n"; }
}

print	"</select><br><br>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$str_EXEC_DELETE_DATA\"$submit_disable>\n".
	"</td>\n".
	"</form>\n";

#--------------------------------------------------------------------------------------

print	"</tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

