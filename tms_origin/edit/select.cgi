#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Time::Local;

use TMSstr;
use TMScommon;
use TMSdeny;
use TMSlock;

use TMSedit;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_CHANGE_LOOM_NAME		= &TMSstr::get_str( "CHANGE_LOOM_NAME"		);
my $str_DELETE_DATA			= &TMSstr::get_str( "DELETE_DATA"		);
my $str_SHIFT_DATA			= &TMSstr::get_str( "SHIFT_DATA"		);
my $str_OPERATOR_DATA			= &TMSstr::get_str( "OPERATOR_DATA"		);
my $str_MONTH				= &TMSstr::get_str( "MONTH"			);
my $str_PERIOD				= &TMSstr::get_str( "PERIOD"			);
my $str_LOOM_NAME			= &TMSstr::get_str( "LOOM_NAME"			);
my $str_CURRENT_LOOM_NAME		= &TMSstr::get_str( "CURRENT_LOOM_NAME"		);
my $str_NEW_LOOM_NAME			= &TMSstr::get_str( "NEW_LOOM_NAME"		);
my $str_SELECT_ALL			= &TMSstr::get_str( "SELECT_ALL"		);
my $str_CHANGE_SELECT_LOOM_NAME_OK	= &TMSstr::get_str( "CHANGE_SELECT_LOOM_NAME_OK");
my $str_DELETE_SELECT_DATA_OK		= &TMSstr::get_str( "DELETE_SELECT_DATA_OK"	);

my $submit_disable = "";
if( &TMSdeny::is_demo_mode() == 1){ $submit_disable = " disabled"; }
elsif( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $update_lock = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){	# データ更新中は使用不可
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

my $html = new CGI;
my $mode     = $html->param('mode');
my $sel_data = $html->param('data');
my $month    = $html->param('month');

# データディレクトリ
my $data_dir;
if( $sel_data eq 'shift'    ){ $data_dir = "..\\..\\tmsdata\\shift";    }
if( $sel_data eq 'operator' ){ $data_dir = "..\\..\\tmsdata\\operator"; }

# 月、期間リスト作成
my @month_list  = ();
my @period_list = ();

$month = &TMSedit::get_month_file_list($month,$data_dir,\@month_list,\@period_list);

# 選択可能な期間に存在する機台名、品種のリストを作成
my @loom_list  = ();
my @style_list = ();	# dummy

&TMSedit::make_edit_index($sel_data,$month,$data_dir,\@period_list,\@loom_list,\@style_list);

#--------------------------------------------------------------------------------

my $tbl_width = 630;
my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

my $colspan = 3;
my $shift_width='33%';

my $title;
my $cgifile;
my $submit_button;

if( $mode eq "rename" ){
  $title = $str_CHANGE_LOOM_NAME;
  $cgifile = 'rename.cgi';
  $submit_button = $str_CHANGE_LOOM_NAME;
}
elsif( $mode eq "delete" ){
  $title = $str_DELETE_DATA;
  $cgifile = 'delete.cgi';
  $submit_button = $str_DELETE_DATA;
}

if( $sel_data eq 'shift'    ){ $title .= " ($str_SHIFT_DATA)";    }
if( $sel_data eq 'operator' ){ $title .= " ($str_OPERATOR_DATA)"; }

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function sel_month() {\n".
	"    i = document.fminput.month.selectedIndex;\n".
	"    val = document.fminput.month.options[i].value;\n".
	"    location.href = \"select.cgi?mode=$mode&data=$sel_data&month=\" + val;\n".
	"  }\n".
	"  function sel_shift() {\n".
	"    document.fminput.all_shift.checked = false;\n".
	"  }\n".
	"  function sel_all_shift() {\n".
	"    len = document.fminput.shift.length;\n".
	"    val = document.fminput.all_shift.checked;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.shift.options[i].selected = val;\n".
	"    }\n".
	"  }\n".
	"  function sel_loom() {\n".
	"    document.fminput.all_loom.checked = false;\n".
	"  }\n".
	"  function sel_all_loom() {\n".
	"    len = document.fminput.loom.length;\n".
	"    val = document.fminput.all_loom.checked;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.loom.options[i].selected = val;\n".
	"    }\n".
	"  }\n".
	"  var submit_disflg = 0;\n".
	"  function disable_submit() {\n";

if( $mode eq "rename" ){
  print	"    res = window.confirm(\"$str_CHANGE_SELECT_LOOM_NAME_OK\");\n".
	"    if( res == false){ return false; }\n".
	"    \n";
}elsif( $mode eq "delete" ){
  print	"    res = window.confirm(\"$str_DELETE_SELECT_DATA_OK\");\n".
	"    if( res == false){ return false; }\n".
	"    \n";
}

print	"    document.fminput.submit.disabled = true;\n".
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
	&TMScommon::make_header('menu','submenu', $lang).

	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return disable_submit()\">\n".
	"<input type=hidden name=\"data\" value=\"$sel_data\">".
	"<table width=$tbl_width><tr align=center><td nowrap><font size=+2><B>$title</B></font></td></tr></table>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".

	"<th><font size=+1 color=white>$str_MONTH</font></th>\n".
	"<th><font size=+1 color=white>$str_PERIOD</font></th>\n".
	"<th><font size=+1 color=white>$str_LOOM_NAME</font></th>\n".

	"</tr>\n".
	"<tr align=center bgcolor=$body_color>\n";

#----------------------------------------------------------------------------
# 月

print	"<td align=center valign=top width=$shift_width>\n".
	"<BR><BR><BR><BR><BR>\n".
	"<select name=\"month\" onChange=\"sel_month()\">\n";

for( my $i=$#month_list; $i>=0; $i-- ){
  my $value = $month_list[$i];
  my @d = split(/\./,$value);
  my $name = "$d[0]/$d[1]";
  if( $value eq $month ){ print "<option value=\"$value\" selected>$name</option>\n"; }
  else{                   print "<option value=\"$value\">$name</option>\n"; }
}

print	"</select>\n".
	"</td>\n";

#----------------------------------------------------------------------------
# シフト、日付

print	"<td align=center width=$shift_width>\n".
	"<select name=\"shift\" size=18 multiple onFocus=\"sel_shift()\">\n";

my @shift_id = &TMScommon::get_shift_id();
for( my $i=$#period_list; $i>=0; $i-- ){
  my $value = $period_list[$i];
  my @d = split(/\./,$value);
  my $name = "$d[0]/$d[1]/$d[2]";
  if( $sel_data eq 'shift' ){ $name .= ".$shift_id[$d[3]]"; }

  # 曜日を作る
  my $y_date = timelocal(0,0,0,$d[2],($d[1] -1),($d[0] -1900));
  my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($y_date);

  my $style = "";
  if(    $wday == 6 ){ $style = " style=\"color=blue\""; }
  elsif( $wday == 0 ){ $style = " style=\"color=red\"" ; }
  print "<option value=\"$value\"$style>$name</option>\n";
}

print	"</select><BR>\n".
	"<input type=CHECKBOX name=\"all_shift\" onClick=\"sel_all_shift()\"><font size=+1><B>$str_SELECT_ALL</B></font>\n".
	"</td>\n";

#----------------------------------------------------------------------------
# 機台名

if( $mode eq "delete" ){
  print	"<td><select name=\"loom\" size=18 multiple onFocus=\"sel_loom()\">\n";

  foreach my $name (@loom_list){
    print "<option value=\"$name\">$name</option>\n";
  }

  print	"</select><br>\n".
	"<input type=CHECKBOX name=\"all_loom\" onClick=\"sel_all_loom()\"><font size=+1><B>$str_SELECT_ALL</B></font>\n".
	"</td>\n";
}
elsif( $mode eq "rename" ){
  print	"<td valign=top >\n".
	"<BR><BR><BR>\n".
	"<font size=+1><B>$str_CURRENT_LOOM_NAME</B></font><BR>\n".
	"<select name=\"loom\">\n";

  foreach my $name (@loom_list){
    print "<option value=\"$name\">$name</option>\n";
  }

  print	"</select><br>\n".
	"<BR><BR><BR>\n".
	"<font size=+1><B>$str_NEW_LOOM_NAME</B></font><BR>\n".
	"<input type=TEXT name=\"new_loom\" size=20>\n".
	"</td>\n";
}
#----------------------------------------------------------------------------

print	"</tr>\n".
	"<tr><td colspan=$colspan align=center bgcolor=$body_color>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\"$submit_disable>\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('submenu','menu', $lang).
	"</center></body></html>\n";
