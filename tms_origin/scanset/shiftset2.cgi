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

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"		);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"		);
my $str_MENU			= &TMSstr::get_str( "MENU"			);
my $str_BACK			= &TMSstr::get_str( "BACK"			);

#######################################################

my $html = new CGI;
my $scanner = $html->param('scanner');

my $shift_schedule_is_week = $html->param('is_week');
my @shift_schedule_simple  = $html->param('simple');
my @shift_schedule_week0   = $html->param('week0');
my @shift_schedule_week1   = $html->param('week1');
my @shift_schedule_week2   = $html->param('week2');
my @shift_schedule_week3   = $html->param('week3');
my @shift_schedule_week4   = $html->param('week4');
my @shift_schedule_week5   = $html->param('week5');
my @shift_schedule_week6   = $html->param('week6');


my @shift_set = ();
$shift_set[0] = "shift_schedule_is_week $shift_schedule_is_week";
$shift_set[1] = &get_schedule_line("shift_schedule_simple", \@shift_schedule_simple);
$shift_set[2] = &get_schedule_line("shift_schedule_week 0", \@shift_schedule_week0);
$shift_set[3] = &get_schedule_line("shift_schedule_week 1", \@shift_schedule_week1);
$shift_set[4] = &get_schedule_line("shift_schedule_week 2", \@shift_schedule_week2);
$shift_set[5] = &get_schedule_line("shift_schedule_week 3", \@shift_schedule_week3);
$shift_set[6] = &get_schedule_line("shift_schedule_week 4", \@shift_schedule_week4);
$shift_set[7] = &get_schedule_line("shift_schedule_week 5", \@shift_schedule_week5);
$shift_set[8] = &get_schedule_line("shift_schedule_week 6", \@shift_schedule_week6);


# 変更前の設定値を読み込み
my @system_set_old = &TMSscanner::get_system_set();


# 変更後の設定ファイルを作成
my @system_set_new = ();
foreach(@system_set_old){
  if( m/^shift_schedule_/ ){ next; }

  push(@system_set_new,$_);
}

push(@system_set_new,@shift_set);


# 設定ファイルをスキャナーに転送
&TMSscanner::upload_scanner_file( "all",
                                  ["set/system_set.txt","set/system_set.update"],
                                  \@system_set_new,     ["update"] );


## 画面表示 ########################################

my $tbl_width = 630;
my $title = $str_SETTING_RESULT;
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR><BR>\n";

  print	"<font size=+2><B>$str_SETTING_SUCCEED</B></font>\n";

print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"<A HREF=\"shiftset.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";


##############################################################################################
# スケジュールの１行データを出力する
# データの整合性も、一部チェックする（時間の逆転まではチェックしてない）

sub get_schedule_line
{
  my($head_str,$r_schedule) = @_;

  my $num = $$r_schedule[0];

  my $data = "";
  for( my $i=0; $i<5; $i++ ){
    my $j = 1+($i*2);
    my $hh = $$r_schedule[$j];
    my $mm = $$r_schedule[$j+1];
    if( ($i >= $num) or (length($hh) <= 0) or (length($mm) <= 0) ){
      $hh = "-1"; $mm = "-1";
      if( $i < $num){ $num = $i; }
    }else{
      $hh = sprintf("%02d",$hh);
      $mm = sprintf("%02d",$mm);
    }
    $data .= " $hh:$mm";
  }

  return $head_str." ".$num.$data;
}

