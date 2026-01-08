#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSdeny;
use TMSlock;

use TMSedit;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SET_STYLE	= &TMSstr::get_str( "SET_STYLE"		);
my $str_SHIFT_DATA	= &TMSstr::get_str( "SHIFT_DATA"	);
my $str_OPERATOR_DATA	= &TMSstr::get_str( "OPERATOR_DATA"	);
my $str_MONTH		= &TMSstr::get_str( "MONTH"		);
my $str_PERIOD		= &TMSstr::get_str( "PERIOD"		);
my $str_OPERATOR	= &TMSstr::get_str( "OPERATOR"		);
my $str_LOOM_NAME	= &TMSstr::get_str( "LOOM_NAME"		);
my $str_STYLE_NAME	= &TMSstr::get_str( "STYLE_NAME"	);
my $str_RESET_MODEIFY	= &TMSstr::get_str( "RESET_MODEIFY"	);

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
my $sel_data = $html->param('data');
my $month    = $html->param('month');
my $loom     = $html->param('loom');

# データディレクトリ
my $data_dir;
if( $sel_data eq 'shift'    ){ $data_dir = "..\\..\\tmsdata\\shift";    }
if( $sel_data eq 'operator' ){ $data_dir = "..\\..\\tmsdata\\operator"; }

# 月、期間リスト作成
my @month_list = ();
my @period_list = ();

$month = &TMSedit::get_month_file_list($month,$data_dir,\@month_list,\@period_list);

# 選択可能な期間に存在する機台名、品種のリストを作成
my @loom_list  = ();
my @style_list = ();	# dummy

&TMSedit::make_edit_index($sel_data,$month,$data_dir,\@period_list,\@loom_list,\@style_list);

#--------------------------------------------------------------------------------
# 機台名のチェック

if( length($loom) > 0 ){
  my $exist_loom = "";
  foreach(@loom_list){ if( $loom eq $_ ){ $exist_loom = $_; last; } }
  $loom = $exist_loom;
}

#--------------------------------------------------------------------------------

my $tbl_width = 630;
my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

my $shift_width='33%';

my $title = $str_SET_STYLE;
if( $sel_data eq 'shift'    ){ $title .= " ($str_SHIFT_DATA)";    }
if( $sel_data eq 'operator' ){ $title .= " ($str_OPERATOR_DATA)"; }

my $cgifile = 'setstyle2.cgi';
my $reset_button = $str_RESET_MODEIFY;
my $submit_button = $str_SET_STYLE;

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
	"    location.href = \"setstyle.cgi?data=$sel_data&month=\" + val + \"&loom=$loom\";\n".
	"  }\n".
	"  function sel_loom() {\n".
	"    i = document.fminput.loom.selectedIndex;\n".
	"    val = document.fminput.loom.options[i].value;\n".
	"    location.href = \"setstyle.cgi?data=$sel_data&month=$month&loom=\" + val;\n".
	"  }\n".
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
	&TMScommon::make_header('menu','submenu', $lang).

	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return disable_submit()\">\n".
	"<input type=hidden name=\"data\" value=\"$sel_data\">".
	"<table width=$tbl_width><tr align=center><td nowrap><font size=+2><B>$title</B></font></td></tr></table>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n";

#----------------------------------------------------------------------------
# 月

print	"<th align=center width=$shift_width nowrap>\n".
	"<font size=+1 color=white>$str_MONTH</font>\n".
	"<select name=\"month\" onChange=\"sel_month()\">\n";

for( my $i=$#month_list; $i>=0; $i-- ){
  my $value = $month_list[$i];
  my @d = split(/\./,$value);
  my $name = "$d[0]/$d[1]";
  if( $value eq $month ){ print "<option value=\"$value\" selected>$name</option>\n"; }
  else{ print "<option value=\"$value\">$name</option>\n"; }
}

print	"</select>\n".
	"</th>\n";

#----------------------------------------------------------------------------
# 機台名

print	"<th align=center width=$shift_width nowrap>\n".
	"<font size=+1 color=white>$str_LOOM_NAME</font>\n".
	"<select name=\"loom\" onChange=\"sel_loom()\">\n";

my $lmlen = length($loom);
if( $lmlen == 0 ){ print "<option value=\"\" selected></option>\n"; }

foreach my $name (@loom_list){
  if( length($name) > 0 ){
    my $selected = "";
    if( $lmlen > 0 ){
      if( $name eq $loom ){ $selected = " selected"; }
    }
    print "<option value=\"$name\"$selected>$name</option>\n";
  }
}

print	"</select>\n".
	"</th>\n".
	"</tr>\n";

#----------------------------------------------------------------------------
# 品種設定画面

if( $lmlen > 0 ){

  my $tbl_width2 = 300;
  my $colspan = 2;

  print	"<tr align=center bgcolor=$body_color><td colspan=$colspan>\n".

	"<table>\n".
	"<th><font size=+1>$str_PERIOD</font></th>\n";

  if( $sel_data eq 'operator' ){
     print	"<th>&nbsp;&nbsp;</th>\n".
     		"<th><font size=+1>$str_OPERATOR</font></th>\n";
  }

  print	"<th>&nbsp;&nbsp;</th>\n".
	"<th><font size=+1>$str_STYLE_NAME</font></th>\n".
	"</tr>\n";

  my @shift_id = &TMScommon::get_shift_id();
  foreach my $fname ( @period_list ){
    if( open(IN,"< $data_dir\\$fname.txt") ){
      while(<IN>){
        my $line = $_;
        my @style = ();
        if( $line =~ m/,mac_name ([^,]+)/ ){
          if( $loom eq $1 ){
            if( $line =~ m/,style ([^,]*)/ ){
              my $style = $1;
              my @d = split(/\./,$fname);
              my $period = "$d[0]/$d[1]/$d[2]";

              if( $sel_data eq 'shift' ){
                $period .= ".$shift_id[$d[3]]";
                print	"<TR><TD><B>$period</B></TD><TD></TD>".
			"<TD><input type=text name=style size=40 value=\"$style\"></TD></TR>\n";
              }
              elsif( $sel_data eq 'operator' ){
                my $ope_name = "";
                if( $line =~ m/,ope_name ([^,]+)/ ){ $ope_name = $1; }
                print	"<TR><TD nowrap><B>$period</B></TD><TD></TD>".
			"<TD nowrap><B>$ope_name</B></TD><TD></TD>".
			"<TD><input type=text name=style size=40 value=\"$style\"></TD></TR>\n";
              }
            }
          }
        }
      }
      close(IN);
    }
  }

  print	"</table></td></tr>\n".
	"<tr><td colspan=$colspan align=center bgcolor=$body_color>\n".
	"<input type=RESET name=\"reset\" value=\"$reset_button\">\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\"$submit_disable>\n".
	"</td></tr>\n";
}

#----------------------------------------------------------------------------

print	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('submenu','menu', $lang).
	"</center></body></html>\n";
