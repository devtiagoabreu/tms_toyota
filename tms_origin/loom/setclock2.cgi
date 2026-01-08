#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Time::Local;

use TMSstr;
use TMScommon;
use TMSlock;
use TMSipset;
use TMSscanner;

$| = 1;
require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_LOOM_CLOCK_SETTING		= &TMSstr::get_str( "LOOM_CLOCK_SETTING"		);
my $str_CANCEL_LOOM_CLOCK_SETTING	= &TMSstr::get_str( "CANCEL_LOOM_CLOCK_SETTING"		);
my $str_SUCCEED				= &TMSstr::get_str( "SUCCEED"				);
my $str_LOOM_CLOCK_IS_WRONG		= &TMSstr::get_str( "LOOM_CLOCK_IS_WRONG"		);
my $str_POWER_OFF			= &TMSstr::get_str( "POWER_OFF"				);
my $str_START_LOOM_CLOCK_SETTING	= &TMSstr::get_str( "START_LOOM_CLOCK_SETTING"		);
my $str_LOOM_CLOCK_SETTING_IS_CANCELED	= &TMSstr::get_str( "LOOM_CLOCK_SETTING_IS_CANCELED"	);
my $str_END_LOOM_CLOCK_SETTING		= &TMSstr::get_str( "END_LOOM_CLOCK_SETTING"		);
my $str_SET_CLOCK			= &TMSstr::get_str( "SET_CLOCK"				);
my $str_NOT_NEED_ADJUST			= &TMSstr::get_str( "NOT_NEED_ADJUST"			);
my $str_TIME_DIFFERENCE			= &TMSstr::get_str( "TIME_DIFFERENCE"			);
my $str_SCANNER				= &TMSstr::get_str( 'SCANNER'				);

my $str_SEC	= &TMSstr::get_str( "SEC"	);
my $str_MINUTE	= &TMSstr::get_str( "MINUITE"	);
my $str_HOUR	= &TMSstr::get_str( "HOUR"	);
my $str_DAY	= &TMSstr::get_str( "DAY"	);
my $str_YEAR	= &TMSstr::get_str( "YEAR"	);

#### httpc.exe のエラー番号に合わせる #####

use constant ERR__PING_TIMEOUT    => 100;
use constant ERR__ARG_ERROR       => 200;
use constant ERR__BAD_HOST_NAME   => 201;
use constant ERR__POST_FILE_ERROR => 210;
use constant ERR__HTTP_NOT_FOUND  => 220;
use constant ERR__HTTP_ERROR      => 300;
use constant ERR__SOCKET_ERROR    => 400;
use constant ERR__PING_ERROR      => 410;
use constant ERR__SYSTEM_ERROR    => 900;

#### setclock2.cgi 独自のエラー番号 ########

use constant ERR__NOT_SUPPORT     => 1000;
use constant ERR__DATA_ERROR      => 1001;

###########################################

my $html = new CGI;

my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

my @ip_list = $html->param('loom');
my @scanner = $html->param('scanner');

if( ($#ip_list < 0) && ($#scanner < 0) ){
  print &TMScommon::no_data_page( $menu_color, $body_color );
  exit;
}

my $other_user;
my $lockfile = 'setclock.lock';
if( &TMSlock::create_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20,\$other_user) ){	# 同時使用を禁止（レベル１）
  print &TMSlock::operation_lock_page( $other_user );
  exit;
}
my $lock_start = time();	# ロック開始時間


my @name_list = ();
&TMSipset::get_name_ip_list( \@name_list, \@ip_list );

# リダイレクトページの表示

my $title = $str_LOOM_CLOCK_SETTING;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function move_next_page() {\n".
	"    location.href = \"setclock3.cgi\";\n".
	"  }\n".
	"  function open_cancel_window() {\n".
	"    window.open(\"cancel.cgi\",\"CancelWindow\",\"width=300,height=150\");\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=$body_color OnLoad=\"setTimeout('move_next_page()',2000)\">\n".
	"<form>\n",
	"&nbsp;&nbsp;&nbsp;&nbsp;<input type=\"button\" value=\"$str_CANCEL_LOOM_CLOCK_SETTING\" onClick=\"open_cancel_window()\"><br>\n".
	"</form>\n".
	"<pre>\n";


my $cancel_file = 'cancel.txt';
if( -f $cancel_file ){ unlink($cancel_file); }
my $cancel_flg = 0;

# ログ用
my $poff_count = 0;	# 電源OFFの機台数
my $same_count = 0;	# 時刻合わせ不要の機台数
my $ok_count   = 0;	# 時刻合わせ成功の機台数
my $err_count  = 0;	# エラーの機台数

&TMScommon::log_entry( "Set Loom Clock Start" );

open(DATA,'> setclock3.dat');
print "**** $str_START_LOOM_CLOCK_SETTING **** \n";

#--------- 機台の時計合わせ -------------------
for( my $i=0; $i<=$#ip_list; $i++ ){

  my $ip = $ip_list[$i];
  my $name = $name_list[$i];
  if( $ip ne $name ){ $name = "$name ($ip)"; }

  my $msg = &adjust_loom_clock($ip);

  print DATA "<tr><td>$name</td><td> ---&gt; $msg</td></tr>\n";
  print "$name ---> $msg\n";

  if( -f $cancel_file ){ $cancel_flg = 1; last; }

  my $now = time();
  if( ($now - $lock_start) >= 10 ){	# 処理開始して１０秒経過したら。
    $lock_start = $now;
    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);  # ロックファイルを更新（レベル１）
  }
}
#--------- スキャナーの時計合わせ -------------
if( $cancel_flg == 0 ){

  foreach my $scan_no (@scanner){

    my $msg = &adjust_scanner_clock($scan_no);

    print DATA "<tr><td>$str_SCANNER $scan_no</td><td> ---&gt; $msg</td></tr>\n";
    print "$str_SCANNER $scan_no ---> $msg\n";

    if( -f $cancel_file ){ $cancel_flg = 1; last; }

    my $now = time();
    if( ($now - $lock_start) >= 10 ){	# 処理開始して１０秒経過したら。
      $lock_start = $now;
      &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);  # ロックファイルを更新（レベル１）
    }
  }
}
#--------- キャンセルの場合 --------------------
if( $cancel_flg ){
  my $msg = $str_LOOM_CLOCK_SETTING_IS_CANCELED;
  print DATA "<tr><td colspan=2 align=center><font color=red><B>*** $msg ****</B></font></td></tr>\n";
  print "<font color=red>**** $msg ****</font>\n";
} else{
  print "**** $str_END_LOOM_CLOCK_SETTING ****\n";
}

close(DATA);

print	"</pre>\n".
	"</body></html>\n";

if( -f $cancel_file ){ unlink($cancel_file); }


# 結果をログファイルに残す
my $log_msg = "Set Loom Clock (OK=$ok_count SAME=$same_count POFF=$poff_count ERR=$err_count)";
if( $cancel_flg ){
  $log_msg .= " and Canceled !!";
}
&TMScommon::log_entry( $log_msg );


unlink($lockfile);	# ロックファイルを削除

exit;


#########################################################################################

sub conv_time_unit
{
  my ($time) = @_;

  my $unit = $str_SEC;

  if( $time >= 60 ){ $time = int($time/60); $unit = $str_MINUTE;
    if( $time >= 60 ){ $time = int($time/60); $unit = $str_HOUR;
      if( $time >= 24 ){ $time = int($time/24); $unit = $str_DAY;
        if( $time >= 365 ){ $time = int($time/365); $unit = $str_YEAR; }
      }
    }
  }
  if( $time <= -60 ){ $time = int($time/60); $unit = $str_MINUTE;
    if( $time <= -60 ){ $time = int($time/60); $unit = $str_HOUR;
      if( $time <= -24 ){ $time = int($time/24); $unit = $str_DAY;
        if( $time <= -365 ){ $time = int($time/365); $unit = $str_YEAR; }
      }
    }
  }

  return "$time $unit";
}

###################################################################################################
# 機台の時刻合わせ
###################################################################################################

sub adjust_loom_clock
{
  my ($host) = @_;

  my $diff;
  my $err = &diff_loom_clock($host, \$diff);	# PC時刻との差を比較

  my $msg = "";
  if( $err == 0 ){	# データ受信成功

    if( (30 >= $diff) && ($diff >= -30) ){  # ずれが30秒以内なら、修正しない
      ++$same_count;
      $msg = "$str_TIME_DIFFERENCE ";
      $msg .= &conv_time_unit($diff);
      $msg .= " -&gt; $str_NOT_NEED_ADJUST";
      return $msg;  # 時刻合わせしない
    }

    $msg .= "<font color=blue>$str_TIME_DIFFERENCE ";
    $msg .= &conv_time_unit($diff);
    $msg .= " -&gt; $str_SET_CLOCK</font> -&gt; ";

    $err = &set_loom_clock($host);		# 機台時刻設定
  }

  if(    $err == 0                   ){ ++$ok_count;   $msg .= $str_SUCCEED; } # 時刻設定成功
  elsif( $err == ERR__PING_TIMEOUT   ){ ++$poff_count; $msg .= "<font color=red>$str_POWER_OFF</font>";  } # pingタイムアウト
  elsif( $err == ERR__PING_ERROR     ){ ++$err_count;  $msg .= "<font color=red>Network ERROR</font>";   } # pingエラー
  elsif( $err == ERR__SOCKET_ERROR   ){ ++$err_count;  $msg .= "<font color=red>Socket ERROR</font>";    }
  elsif( $err == ERR__HTTP_ERROR     ){ ++$err_count;  $msg .= "<font color=red>HTTP ERROR</font>";      }
  elsif( $err == ERR__HTTP_NOT_FOUND ){ ++$err_count;  $msg .= "<font color=red>HTTP ERROR (not found)</font>"; }
  elsif( $err == ERR__NOT_SUPPORT    ){ ++$err_count;  $msg .= "<font color=red>Not Support TMS</font>"; }
  elsif( $err == ERR__DATA_ERROR     ){ ++$err_count;  $msg .= "<font color=red>Data ERROR</font>";      }
  else{                                 ++$err_count;  $msg .= "<font color=red>System ERROR</font>";    } # システム関係のエラー

  return $msg;
}

#########################################################################################

sub diff_loom_clock
{
  my ($host, $r_diff) = @_;

  my $path = "/cgi-bin/ext.cgi?func=tms_get_monitor_data&data1=current";

  # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
  if( ! open(PIPE,"..\\bin\\httpc.exe \"$host\" \"$path\" |" ) ){
    return ERR__SYSTEM_ERROR;
  }
  my @tmsdata = <PIPE>;
  close(PIPE);

  if( $? != 0 ){  # httpc.exe 失敗
    if( defined($tmsdata[0]) ){
      if( $tmsdata[0] =~ m/^(\d{3})\s/ ){  # １行目の先頭が３桁の数字なら
        return int($1);
      }
    }
    return ERR__SYSTEM_ERROR;
  }

  # ここから httpc.exe 成功時

  # １行目チェック
  if( $#tmsdata < 0 ){ return ERR__DATA_ERROR; }
  if( $tmsdata[0] =~ m/^Not supported\./             ){ return ERR__NOT_SUPPORT; }
  if( $tmsdata[0] =~ m/^func\(command\) not found\./ ){ return ERR__NOT_SUPPORT; }

  my $sh_flg = 0;
  my $op_flg = 0;

  ## データ先頭の５行を調べ start_time を取得
  if( $#tmsdata < 5 ){ return ERR__DATA_ERROR; }
  for( my $i=0; $i<5; $i++ ){
    my $line = splice( @tmsdata, 0, 1 );  # 配列の先頭を取り出す

    if( $line =~ m/^Not supported\./             ){ return ERR__NOT_SUPPORT; }
    if( $line =~ m/^func\(command\) not found\./ ){ return ERR__NOT_SUPPORT; }

    if(    $line =~ m/^shift_start_time /    ){ $sh_flg = 1; }
    elsif( $line =~ m/^operator_start_time / ){ $op_flg = 1; }

    if( $sh_flg && $op_flg ){ last; }
  }
  if( ($sh_flg == 0) or ($op_flg == 0) or ($#tmsdata < 3) ){ return ERR__DATA_ERROR; }


  # 機台の時計とPCの時計を比較
  my $pc_date = time();

  foreach my $line (@tmsdata){
    if( $line =~ m/^sys_time / ){
      my @d = split(/ /,$line);
      my $sys_date = timelocal($d[7],$d[6],$d[5],$d[3],($d[2] -1),($d[1] -1900));
      $$r_diff = $sys_date - $pc_date;
      return 0;  # 成功
    }
    if( $line =~ m/^#end_of_data/ ){ last; }
  }

  return ERR__DATA_ERROR;  # sys_time が無い！！
}

#########################################################################################

sub set_loom_clock
{
  my ($host) = @_;

  my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
  my $set_time = sprintf("%d+%d+%d+%d+%d+%d",($year+1900),($mon+1),$mday,$hour,$min,$sec);

  my $path = "/cgi-bin/ext.cgi?func=tms_set_date&data=$set_time";

  # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
  if( ! open(PIPE,"..\\bin\\httpc.exe \"$host\" \"$path\" |") ){
    return ERR__SYSTEM_ERROR;
  }
  my @data = <PIPE>;
  close(PIPE);

  if( $? != 0 ){  # httpc.exe 失敗
    if( defined($data[0]) ){
      if( $data[0] =~ m/^(\d{3})\s/ ){  # １行目の先頭が３桁の数字なら
        return int($1);
      }
    }
    return ERR__SYSTEM_ERROR;
  }

  # ここから httpc.exe 成功時
  foreach(@data){
    if( m/^Not supported\./             ){ return ERR__NOT_SUPPORT; }
    if( m/^func\(command\) not found\./ ){ return ERR__NOT_SUPPORT; }
    if( m/^OK/                          ){ return 0; }
  }

  return ERR__DATA_ERROR;
}

#########################################################################################
# スキャナーの時刻合わせ
#########################################################################################

sub adjust_scanner_clock
{
  my ($scan_no) = @_;

  my $diff;
  my $err = &diff_scanner_clock($scan_no, \$diff);	# PC時刻との差を比較

  my $msg = "";
  if( $err == 0 ){	# データ受信成功

    if( (30 >= $diff) && ($diff >= -30) ){  # ずれが30秒以内なら、修正しない
      ++$same_count;
      $msg = "$str_TIME_DIFFERENCE ";
      $msg .= &conv_time_unit($diff);
      $msg .= " -&gt; $str_NOT_NEED_ADJUST";
      return $msg;  # 時刻合わせしない
    }

    $msg .= "<font color=blue>$str_TIME_DIFFERENCE ";
    $msg .= &conv_time_unit($diff);
    $msg .= " -&gt; $str_SET_CLOCK</font> -&gt; ";

    $err = &set_scanner_clock($scan_no);	# 機台時刻設定
  }

  # ＜補足＞ 通信エラー等は、get_scanner_file のエラー画面で表示されるので、ここは DATA_ERROR のみ

  if( $err == 0 ){ ++$ok_count;   $msg .= $str_SUCCEED;                        } # 時刻設定成功
  else{            ++$err_count;  $msg .= "<font color=red>Data ERROR</font>"; } # データ内容が不正

  return $msg;
}

#########################################################################################

sub diff_scanner_clock
{
  my ($scan_no, $r_diff) = @_;

  my @data = &TMSscanner::get_scanner_file($scan_no,"cgi-bin/scanset.cgi?func=systime");

  # 機台の時計とPCの時計を比較
  if( defined($data[0]) ){
    if( $data[0] =~ m/^([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)/ ){
      my $sys_date = timelocal($6,$5,$4,$3,($2 -1),($1 -1900));
      my $pc_date = time();
      $$r_diff = $sys_date - $pc_date;
      return 0;  # 成功
    }
  }

  return ERR__DATA_ERROR;
}

#########################################################################################

sub set_scanner_clock
{
  my ($scan_no) = @_;

  my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
  my $set_time = sprintf("%d+%d+%d+%d+%d+%d",($year+1900),($mon+1),$mday,$hour,$min,$sec);

  my @data = &TMSscanner::get_scanner_file( $scan_no, "cgi-bin/scanset.cgi?func=systime&set_time=$set_time" );

  if( defined($data[0]) ){
    if( $data[0] =~ m/^OK/ ){ return 0; }  # 成功
  }

  return ERR__DATA_ERROR;
}

#########################################################################################

