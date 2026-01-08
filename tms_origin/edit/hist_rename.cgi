#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Time::Local;

use TMSstr;
use TMScommon;
use TMSdeny;
use TMSlock;
use TMSstophist;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_CHANGE_LOOM_NAME		= &TMSstr::get_str( "CHANGE_LOOM_NAME"		);
my $str_STOP_HISTORY			= &TMSstr::get_str( "STOP_HISTORY"		);
my $str_MONTH				= &TMSstr::get_str( "MONTH"			);
my $str_PERIOD				= &TMSstr::get_str( "PERIOD"			);
my $str_LOOM_NAME			= &TMSstr::get_str( "LOOM_NAME"			);
my $str_CURRENT_LOOM_NAME		= &TMSstr::get_str( "CURRENT_LOOM_NAME"		);
my $str_NEW_LOOM_NAME			= &TMSstr::get_str( "NEW_LOOM_NAME"		);
my $str_SELECT_ALL			= &TMSstr::get_str( "SELECT_ALL"		);
my $str_CHANGE_SELECT_LOOM_NAME_OK	= &TMSstr::get_str( "CHANGE_SELECT_LOOM_NAME_OK");

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
my $month = $html->param('month');
if( !defined($month) ){ $month = ""; }

# 停止履歴フォルダの一覧を取得
my ($stophist_dir, @stophist_subdir) = &TMSstophist::get_stophist_dir();
@stophist_subdir = sort {$b cmp $a} @stophist_subdir;  # 逆順ソート

# 月が指定されてなければ、最初の月とする
if( ($month eq "") and ($#stophist_subdir >= 0) ){
  $month = substr( $stophist_subdir[0], 0, 7 ); # yyyy.mm
}

### 期間（yyyy.mm）の一覧作成 ###
my @month_list  = ();
my @period_list = ();

my $prev_ym = "";
foreach my $subdir ( @stophist_subdir ){
  my $ym = substr( $subdir, 0, 7 );  # "yyyy.mm"

  # 期間（yyyy.mm）のリスト登録、重複は除く
  if( $ym ne $prev_ym ){
    push( @month_list, $ym );
    $prev_ym = $ym;
  }

  # 選択された月に属する履歴元フォルダを取得
  if( $ym eq $month ){
    push( @period_list, $subdir );
  }
}

### 選択された月に存在する機台名を取得 ###
my %macname_hash = ();
foreach my $subdir ( @period_list ){

  # indexファイルから機台名を読み取る
  if( open(INDEX, "< $stophist_dir\\$subdir\\index.txt") ){
    while(<INDEX>){
      chomp $_;

      my @element = split(/,/, $_);
      if( defined($element[2]) ){
        my $macname = $element[2];  # 機台名は第3項目
        if( $macname !~ m/^\s*$/ ){ # 空白、スペース、タブ以外

          # 機台名を重複を除く為、一度連想配列に登録
          $macname_hash{$macname} = 1;
        }
      }
    }
    close(INDEX);
  }

}
my @loom_list = sort keys %macname_hash;


#--------------------------------------------------------------------------------

my $tbl_width = 630;
my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

my $colspan = 3;
my $shift_width='33%';

my $title         = $str_CHANGE_LOOM_NAME.'('.$str_STOP_HISTORY.')';
my $mycgifile     = 'hist_rename.cgi';
my $cgifile_togo  = 'hist_rename2.cgi';
my $submit_button = $str_CHANGE_LOOM_NAME;

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
	"    location.href = \"$mycgifile?month=\" + val;\n".
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
	"  var submit_disflg = 0;\n".
	"  function disable_submit() {\n".
	"    res = window.confirm(\"$str_CHANGE_SELECT_LOOM_NAME_OK\");\n".
	"    if( res == false){ return false; }\n".
	"    \n".
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

	"<form name=\"fminput\" action=\"$cgifile_togo\" method=POST onSubmit=\"return disable_submit()\">\n".
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
  else{ print "<option value=\"$value\">$name</option>\n"; }
}

print	"</select>\n".
	"</td>\n";

#----------------------------------------------------------------------------
# 日付

print	"<td align=center width=$shift_width>\n".
	"<select name=\"shift\" size=18 multiple onFocus=\"sel_shift()\">\n";

foreach my $period ( @period_list){ # yyyy.mm.dd
  my @d = split(/\./,$period);   # yyyy, mm, dd
  my $name = "$d[0]/$d[1]/$d[2]";

  # 曜日を作る
  my $y_date = timelocal(0,0,0,$d[2],($d[1] -1),($d[0] -1900));
  my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($y_date);

  my $style = "";
  if(    $wday == 6 ){ $style = " style=\"color=blue\""; }
  elsif( $wday == 0 ){ $style = " style=\"color=red\"" ; }
  print "<option value=\"$period\"$style>$name</option>\n";
}

print	"</select><BR>\n".
	"<input type=CHECKBOX name=\"all_shift\" onClick=\"sel_all_shift()\"><font size=+1><B>$str_SELECT_ALL</B></font>\n".
	"</td>\n";

#----------------------------------------------------------------------------
# 機台名


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

#----------------------------------------------------------------------------

print	"</tr>\n".
	"<tr><td colspan=$colspan align=center bgcolor=$body_color>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\"$submit_disable>\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('submenu','menu', $lang).
	"</center></body></html>\n";
