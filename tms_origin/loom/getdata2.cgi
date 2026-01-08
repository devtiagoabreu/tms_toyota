#! C:\Perl\bin\perl.exe -I..\common

use strict;
no strict "refs";	# for open($fd,'httpc.exe |')
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Time::Local;

use TMSstr;
use TMScommon;
use TMSlock;
use TMScollect;
use TMSrestruct;
use TMSipset;
use TMSscanner;
use TMSDATAnew;
use TMSDATAmerge;
use TMSDATAfinal;
use TMSDATAindex;

$| = 1;
require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_DATA_COLLECTION_NETWORK		= &TMSstr::get_str( "DATA_COLLECTION_NETWORK"		);
my $str_CANCEL_DATA_COLLECTING		= &TMSstr::get_str( "CANCEL_DATA_COLLECTING"		);
my $str_SUCCEED				= &TMSstr::get_str( "SUCCEED"				);
my $str_LOOM_CLOCK_IS_WRONG		= &TMSstr::get_str( "LOOM_CLOCK_IS_WRONG"		);
my $str_POWER_OFF			= &TMSstr::get_str( "POWER_OFF"				);
my $str_START_DATA_COLLECTING		= &TMSstr::get_str( "START_DATA_COLLECTING"		);
my $str_DATA_COLLECTING_IS_CANCELED	= &TMSstr::get_str( "DATA_COLLECTING_IS_CANCELED"	);
my $str_END_DATA_COLLECTING		= &TMSstr::get_str( "END_DATA_COLLECTING"		);
my $str_NO_DATA_COLLECTED		= &TMSstr::get_str( "NO_DATA_COLLECTED"			);
my $str_START_DATA_CONVERTING		= &TMSstr::get_str( "START_DATA_CONVERTING"		);
my $str_COMPLETED_ALL_PROPERLY		= &TMSstr::get_str( "COMPLETED_ALL_PROPERLY"		);


################################################################

my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

my $html = new CGI;

my @loom_id_name = $html->param('loom');
if( $#loom_id_name < 0 ){
  print &TMScommon::no_data_page( $menu_color, $body_color );
  exit;
}


my $lockfile = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::create_lockfile($lockfile,$ENV{REMOTE_ADDR},1,60,\$other_user) ){	# 同時使用を禁止（レベル１）
  print &TMSlock::data_updating_page( $other_user );
  exit;
}
my $lock_start = time();	# ロック開始時間

### リダイレクトページの表示 #####

my $title = $str_DATA_COLLECTION_NETWORK;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function move_next_page() {\n".
	"    location.href = \"getdata3.cgi\";\n".
	"  }\n".
	"  function open_cancel_window() {\n".
	"    window.open(\"cancel.cgi\",\"CancelWindow\",\"width=300,height=150\");\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=$body_color OnLoad=\"setTimeout('move_next_page()',2000)\">\n".
	"<form>\n",
	"&nbsp;&nbsp;&nbsp;&nbsp;<input type=\"button\" value=\"$str_CANCEL_DATA_COLLECTING\" onClick=\"open_cancel_window()\"><br>\n".
	"</form>\n".
	"<pre>\n";

&TMScommon::make_dir( "..\\..\\tmsdata" );
my $data_dir = "..\\..\\tmsdata\\loom";
&TMScommon::make_dir( $data_dir );
# (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
system( "del /Q /F $data_dir\\*.*" );

#------------------------------------------------------------------------------------
# データ収集

my $cancel_file = 'cancel.txt';
if( -f $cancel_file ){ unlink($cancel_file); }
my $cancel_flg = 0;


&TMScommon::log_entry( "Get Network TMS Data Start" );

open(DATA,'> getdata3.dat');
print "**** $str_START_DATA_COLLECTING **** \n";

# ログ用（カウントアップは、print_result 内で）
my $get_count  = 0;   # データ取得総数
my $ok_count   = 0;   # データ収集成功機台数
my $poff_count = 0;   # 電源OFF機台数
my $warn_count = 0;   # 時刻ずれ機台数
my $err_count  = 0;   # エラー機台数


#### スキャナー、JAT710毎に対象機台を分離する ####
my @scan1_loom = ();
my @scan2_loom = ();
my @scan3_loom = ();
my @scan4_loom = ();
my @scan5_loom = ();
my @jat710_loom = ();

foreach( @loom_id_name ){
  my ($id, $name) = split(/ /,$_,2);

  if( $id =~ m/^S([1-5])-/ ){
    if(    $1 == 1 ){ push( @scan1_loom, [$id,$name] ); }
    elsif( $1 == 2 ){ push( @scan2_loom, [$id,$name] ); }
    elsif( $1 == 3 ){ push( @scan3_loom, [$id,$name] ); }
    elsif( $1 == 4 ){ push( @scan4_loom, [$id,$name] ); }
    elsif( $1 == 5 ){ push( @scan5_loom, [$id,$name] ); }
  }
  else{
    push( @jat710_loom, [$id,$name] );
  }
}

### スキャナーのIPリスト
my @scan_ip = &TMSscanner::get_scan_ip();

if( $#scan1_loom >= 0 ){
  &get_scan_tms_data( $scan_ip[0], \@scan1_loom );
}
if( $#scan2_loom >= 0 ){
  &get_scan_tms_data( $scan_ip[1], \@scan2_loom );
}
if( $#scan3_loom >= 0 ){
  &get_scan_tms_data( $scan_ip[2], \@scan3_loom );
}
if( $#scan4_loom >= 0 ){
  &get_scan_tms_data( $scan_ip[3], \@scan4_loom );
}
if( $#scan5_loom >= 0 ){
  &get_scan_tms_data( $scan_ip[4], \@scan5_loom );
}

if( $#jat710_loom >= 0 ){
  &get_jat710_tms_data( \@jat710_loom );
}

#------------------------------------------------------------------------------------
# データ収集結果をログファイルに残す

my $log_msg = "Get Network TMS Data (OK=$ok_count WARN=$warn_count POFF=$poff_count ERR=$err_count)";
if( $cancel_flg ){
  $log_msg .= " and Canceled !!";
}
&TMScommon::log_entry( $log_msg );


#------------------------------------------------------------------------------------
# データ収集をキャンセルされた場合、有効なデータが無い場合

if( $cancel_flg ){
  my $msg = $str_DATA_COLLECTING_IS_CANCELED;
  print DATA "<tr><td colspan=2 align=center><font color=red><B>*** $msg ****</B></font></td></tr>\n";
  print "<font color=red>**** $msg ****</font>\n";
} else{
  print "**** $str_END_DATA_COLLECTING ****\n";
  if( $get_count == 0 ){
    my $msg = $str_NO_DATA_COLLECTED;
    print DATA "<tr><td colspan=2 align=center><font color=red><B>*** $msg ****</B></font></td></tr>\n";
    print "<font color=red>**** $msg ****</font>\n";
  }
}

#------------------------------------------------------------------------------------
# スキャナーデータのBACKUP

my $backup_dir = "..\\..\\tmsdata\\backup";
&TMScommon::make_dir($backup_dir);

if( $cancel_flg == 0 ){
  for( my $i=0; $i<=$#scan_ip; $i++ ){
    if( defined($scan_ip[$i]) ){

      # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
      my $cmd = "..\\bin\\httpc.exe $scan_ip[$i] \"/TmsScanner/backup.zip\" > $backup_dir\\scanner.tmp";
      if( system( $cmd ) == 0 ){  # httpc.exe 成功
        rename("$backup_dir\\scanner.tmp", "$backup_dir\\scanner".($i+1).".zip");
      }else{  # 失敗
        unlink("$backup_dir\\scanner.tmp");
        &TMScommon::log_entry( "Scanner".($i+1)." Data Backup Fail" );
      }
    }
  }
}

#------------------------------------------------------------------------------------
# 収集したデータの処理

if( ($cancel_flg == 0) && ($get_count > 0) ){

  print "**** $str_START_DATA_CONVERTING ****\n";

  &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);	# ロックファイルを更新（レベル１）

  &TMSDATAnew::make_newdata( 1 );  # Phase 1

  &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);	# ロックファイルを更新（レベル１）

  &TMSDATAmerge::merge_data( 2 );  # Phase 2

  &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);	# ロックファイルを更新（レベル１）

  if( &TMSrestruct::check_restruction() ){	# 再構築が必要の場合
    &TMSDATAfinal::update_all_request();	# 全体を再構築
    &TMSrestruct::clr_restruction_request();	# 再構築要求ファイルを削除
  }
  &TMSDATAfinal::make_final( 3 );  # Phase 3

  &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);	# ロックファイルを更新（レベル１）

  &TMSDATAindex::make_index( 4 );  # Phase 4

  &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);	# ロックファイルを更新（レベル１）

  &TMSstophist::make_stophist_csv( 5 );  # Phase 5

  my $msg = $str_COMPLETED_ALL_PROPERLY;
  print DATA "<tr><td colspan=2 align=center><B>*** $msg ****</B></td></tr>\n";
  print "**** $msg ****\n";

  # データ収集時間を更新
  &TMScollect::update_collect_date();

  # データ処理終了のログ
  &TMScommon::log_entry( "End Data Convert" );
}

close(DATA);

print	"</pre>\n".
	"</body></html>\n";

if( -f $cancel_file ){ unlink($cancel_file); }

unlink($lockfile);	# ロックファイルを削除

exit;

#########################################################################################
#########################################################################################
# スキャナーからのデータ収集

#### httpc.exe のエラー番号(100-999) #####

use constant ERR__PING_TIMEOUT    => 100;
use constant ERR__ARG_ERROR       => 200;
use constant ERR__BAD_HOST_NAME   => 201;
use constant ERR__POST_FILE_ERROR => 210;
use constant ERR__HTTP_NOT_FOUND  => 220;
use constant ERR__HTTP_ERROR      => 300;
use constant ERR__SOCKET_ERROR    => 400;
use constant ERR__PING_ERROR      => 410;
use constant ERR__SYSTEM_ERROR    => 900;

#### getdata2.cgi 独自のエラー番号 ########

use constant ERR__NOT_SUPPORT     => 1000;
use constant ERR__START_TIME_DIFF => 1001;
use constant ERR__DATA_ERROR      => 1002;

use constant WARN__CLOCK_DIFF     => 1100;

###########################################

## 同時取機台得数 ##
use constant MGET_MAX => 10;

sub get_scan_tms_data
{
  my ($scan_ip,$r_loom) = @_;

  # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
  my $path = "/TmsScanner/cgi-bin/mget_tmsdata.cgi";

  ### ファイル区切り文字列 ###
  my $boundary_str = "----------mget-boundary-strings----------";

  my $loom_pos = 0;
  while( $loom_pos <= $#$r_loom ){

    # ---- 中断されてないかチェック ----
    if( $cancel_flg ){ last; }
    elsif( -f $cancel_file ){ $cancel_flg = 1; last; }

    my @get_list = ();
    my %err_list = ();  # エラー処理用 (key = mac_id)

    # ---- POSTデータを生成 ----
    my $post_data = "boundary=".$boundary_str;

    for( my $i=0; $i<MGET_MAX; $i++ ){
      my ($mac_id,$name) = @{$$r_loom[$loom_pos++]};

      $post_data .= "&mac_id=$mac_id";

      push(@get_list,[$mac_id,$name]);
      $err_list{$mac_id} = ERR__SYSTEM_ERROR;  # デフォルトのエラー

      if( $loom_pos > $#$r_loom ) { last; }
    }

    # ---- POSTデータを一時ファイルに書き込む ----

    my $post_file = &TMScommon::get_tmp_file_name("moni_post");
    if( open(FILE,"> $post_file") ){
      binmode(FILE);  # バイナリーモードにする
      print FILE $post_data;
      close(FILE);

      # ---- データを取得する ----

      # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
      if( open(PIPE,"..\\bin\\httpc.exe \"$scan_ip\" \"$path\" \"\" $post_file |") ){
        my @data = <PIPE>;
        close(PIPE);

        if( $? != 0 ){  # httpc.exe 失敗
          if( defined($data[0]) ){
            if( $data[0] =~ m/^(\d{3})\s/ ){  # 先頭が３桁の数字なら
              my $err = int($1);
              foreach(@get_list){
                my ($mac_id,$name) = @$_;
                $err_list{$mac_id} = $err;  # 同じエラーを登録
              }
            }
          }
        }
        else{  # httpc.exe 成功

          my @each_data;  # １台毎のデータ
          my $boundary_level = 0;
          my $mac_id = "";

          foreach(@data){
            if( $boundary_level == 1 ){  # 区切り文字の直後の行は、機台ID
              chomp;
              $mac_id = $_;

              $boundary_level = 2;
              @each_data = ();
            }
            elsif( $boundary_level == 2 ){  # データ行
              if( $_ eq "$boundary_str\n" ){
                if( $#each_data >= 0 ){
                  chomp $each_data[$#each_data];  # 最後の行をの改行コードを削除
                  if( length($each_data[$#each_data]) == 0 ){
                    $#each_data = $#each_data -1;  # 最後の行を削除(区切り文字の一部なので)
                  }
                }
                $err_list{$mac_id} = &check_monitor_data(\@each_data);

                $boundary_level = 1;
              }else{
                push(@each_data, $_);  # データの取り込み
              }
            }else{
              if( $_ eq "$boundary_str\n" ){
                $boundary_level = 1;
              }
            }
          }
        }
      }
    }
    unlink($post_file);  # 一時ファイルを削除

    # ---- 結果の表示 ----
    foreach(@get_list){
      my ($mac_id,$name) = @$_;
      my $err = $err_list{$mac_id};
      my ($html_msg,$text_msg) = &get_result_msg($mac_id,$name,$err,0);
      print DATA $html_msg;
      print $text_msg;
    }

    # ---- ロック時間を更新 ----
    my $now = time();
    if( ($now - $lock_start) >= 10 ){	# 処理開始して１０秒経過したら。
      $lock_start = $now;
      &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,60);  # ロックファイルを更新（レベル１）
    }

  }
}

#########################################################################################
# ＪＡＴ７１０機台からのデータ収集

## 同時接続数 ##
use constant PIPE_MAX => 10;

sub get_jat710_tms_data
{
  my ( $r_loom ) = @_;

  # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
  my $path = "/cgi-bin/ext.cgi?func=tms_get_monitor_data&data1=current&data2=monitor&data3=shift&data4=history";

  my @get_list = ();  # 同時に取得する対象のリスト（２重配列）

  # ---- １回目のデータ取得処理 ----

  my $loom_pos = 0;
  while( ($loom_pos < PIPE_MAX) and ($loom_pos <= $#$r_loom) ){

    my ($ip,$name) = @{$$r_loom[$loom_pos++]};

    my $num = sprintf("%02d",$loom_pos);
    my $pipe = "PIPE$num";
    my $tmpfile = "$data_dir\\tmpdat$num.tmp";

    if( open($pipe,"..\\bin\\httpc.exe \"$ip\" \"$path\" > \"$tmpfile\" |") ){ # 外部プログラム起動
      push(@get_list,[$ip,$name,$pipe,$tmpfile,0]);  # リトライ回数=0
    }
  }

  # ---- httpc.exe の終了を待ち、結果を順に処理していく ----

  while( $#get_list >= 0 ){

    my @next_list = ();  # 次のデータ取得用

    for( my $i=0; $i<=$#get_list; $i++ ){

      my ($ip,$name,$pipe,$tmpfile,$retry) = @{$get_list[$i]};

      my $dummy = <$pipe>;  # httpc.exe の終了を待つ
      close($pipe);

      # ---- 取得したデータの処理 ----
      my $result = ERR__SYSTEM_ERROR;
      my $retry_flg = 0;

      if( open(FILE, "< $tmpfile") ){  # 一時ファイルを開く
        my @tmpdata = <FILE>;
        close(FILE);

        if( $? == 0 ){  # httpc.exe 成功
          $result = &check_monitor_data(\@tmpdata);
          if( ($result == ERR__START_TIME_DIFF) and ($retry == 0) ){
            $retry_flg = 1;  # 上記のエラーの場合のみリトライする
          }
        }
        else{  # httpc.exe 失敗
          $result = &check_error_data(\@tmpdata);
        }
      }
      unlink($tmpfile);  # 一時ファイルを消す

      # ---- 結果の表示 ----
      if( $retry_flg == 0 ){
        my ($html_msg,$text_msg) = &get_result_msg($ip,$name,$result,$retry);
        print DATA $html_msg;
        print $text_msg;
      }

      # ---- 中断されてないかチェック ----
      if( $cancel_flg == 0 ){
        if( -f $cancel_file ){ $cancel_flg = 1; }
      }

      # ---- 次のデータ取得処理を始める ----
      if( $cancel_flg == 0){
        if( $retry_flg ){
          if( open($pipe,"..\\bin\\httpc.exe \"$ip\" \"$path\" > \"$tmpfile\" |") ){ # 外部プログラム起動
            push( @next_list, [$ip,$name,$pipe,$tmpfile,1] );  # リトライ回数=1
          }
        }
        elsif( $loom_pos <= $#$r_loom ){
          ($ip,$name) = @{$$r_loom[$loom_pos++]};  # 次の対象機台

          if( open($pipe,"..\\bin\\httpc.exe \"$ip\" \"$path\" > \"$tmpfile\" |") ){ # 外部プログラム起動
            push(@next_list,[$ip,$name,$pipe,$tmpfile,0]);  # リトライ回数=0
          }
        }
      }
    }

    @get_list = @next_list;

    # ---- ロック時間を更新 ----
    my $now = time();
    if( ($now - $lock_start) >= 10 ){	# 処理開始して１０秒経過したら。
      $lock_start = $now;
      &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,60);  # ロックファイルを更新（レベル１）
    }
  }
}


#########################################################################################
#########################################################################################

sub check_monitor_data
{
  my ($r_tmsdata) = @_;

  # １行目チェック
  if( $#$r_tmsdata < 0 ){ return ERR__DATA_ERROR; }
  if( $$r_tmsdata[0] =~ m/^Not supported\./             ){ return ERR__NOT_SUPPORT; }
  if( $$r_tmsdata[0] =~ m/^func\(command\) not found\./ ){ return ERR__NOT_SUPPORT; }

  my $hi_st_tm = "";
  my $sh_st_tm = "";
  my $op_st_tm = "";
  my $hi_flg = 0;
  my $sh_flg = 0;
  my $op_flg = 0;

  ## データ先頭の５行を調べ start_time を取得
  if( $#$r_tmsdata < 5 ){ return ERR__DATA_ERROR; }
  for( my $i=0; $i<5; $i++ ){
    my $line = splice( @$r_tmsdata, 0, 1 );  # 配列の先頭を取り出す

    if(    $line =~ m/^history_start_time /  ){ $hi_st_tm = $line; $hi_flg = 1; } # add 2005.6.7
    elsif( $line =~ m/^shift_start_time /    ){ $sh_st_tm = $line; $sh_flg = 1; }
    elsif( $line =~ m/^operator_start_time / ){ $op_st_tm = $line; $op_flg = 1; }

    if( $sh_flg && $op_flg ){ last; }  # 古い機台に対応する為、$hi_flg は見ない
  }
  if( ($sh_flg == 0) or ($op_flg == 0) or ($#$r_tmsdata < 3) ){ return ERR__DATA_ERROR; }


  # データ先頭と末尾の start_time を比較
  # (データが途中で切れた場合も、ERR__START_TIME_DIFF とする)

  if( $hi_flg ){  # 停止履歴ある場合（ add 2005.6.7 ）
    $hi_flg = 0;
    $sh_flg = 0;
    $op_flg = 0;
    my @tail = splice( @$r_tmsdata, -3 );  # 配列の最後の３行を取り出す
    foreach my $line ( @tail ){
      if(    $line =~ m/^history_start_time /  ){ if( $line eq $hi_st_tm ){ $hi_flg = 1; } }
      elsif( $line =~ m/^shift_start_time /    ){ if( $line eq $sh_st_tm ){ $sh_flg = 1; } }
      elsif( $line =~ m/^operator_start_time / ){ if( $line eq $op_st_tm ){ $op_flg = 1; } }
    }
    if( ($hi_flg == 0) or ($sh_flg == 0) or ($op_flg == 0) ){ return ERR__START_TIME_DIFF; }
  }
  else{  # 停止履歴無い場合（古い機台）
    $sh_flg = 0;
    $op_flg = 0;
    my @tail = splice( @$r_tmsdata, -2 );  # 配列の最後の２行を取り出す
    foreach my $line ( @tail ){
      if(    $line =~ m/^shift_start_time /    ){ if( $line eq $sh_st_tm ){ $sh_flg = 1; } }
      elsif( $line =~ m/^operator_start_time / ){ if( $line eq $op_st_tm ){ $op_flg = 1; } }
    }
    if( ($sh_flg == 0) or ($op_flg == 0) ){ return ERR__START_TIME_DIFF; }
  }

  # ------------------------------------------------------------------------------
  # ip_addr の行を読み出し

  my $ip_addr = "";
  foreach( @$r_tmsdata ){
    my $line = $_;

    if( $line =~ m/^ip_addr\s+(.+)$/ ){ $ip_addr = $1; last; }
    if( $line =~ m/^#end_of_data/ ){ return ERR__DATA_ERROR; }
  }

  # ------------------------------------------------------------------------------
  # データ取得日（get_time）

  my $pc_date = time();
  my $get_time;
  {
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($pc_date);
    $get_time = sprintf("%d %d %d %d %d %d %d",($year+1900),($mon+1),$mday,$wday,$hour,$min,$sec);
  }

  # ------------------------------------------------------------------------------
  # データをファイルに保存（データ中の ip_addr からファイル名を作成）

  $ip_addr =~ s/\n$//;	# 改行コードを削除。
  $ip_addr =~ s/\s//g;	# スペースを削除する。

  if( length($ip_addr) <= 0 ){ return ERR__DATA_ERROR; }
  else{

    my $fname;
    if( $ip_addr =~ m/^([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)$/ ){
      $fname = sprintf("%03d%03d%03d%03d.txt", $1,$2,$3,$4);
    }else{
      $fname = $ip_addr;
      $fname =~ s/\.//g;
      $fname = $fname.".txt";
    }

    open(FILE,"> $data_dir\\$fname");
    print FILE "get_time $get_time\n";
    print FILE @$r_tmsdata;
    close(FILE);
  }

  # ------------------------------------------------------------------------------
  # 機台の時計とPCの時計を比較

  foreach( @$r_tmsdata ){
    my $line = $_;

    if( $line =~ m/^sys_time / ){
      $line =~ s/\n$//;		# 改行コードを削除。
      $line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
      my @d = split(/ /,$line);
      my $sys_date = timelocal($d[7],$d[6],$d[5],$d[3],($d[2] -1),($d[1] -1900));
      my $diff = $sys_date - $pc_date;
      if( ($diff > 600) || (-600 > $diff) ){ return WARN__CLOCK_DIFF; }
      last;
    }
    if( $line =~ m/^#end_of_data/ ){ last; }
  }

  return 0;  # ＯＫ
}

#########################################################################################

sub check_error_data
{
  my ($r_errdata) = @_;

  if( defined(${$r_errdata}[0]) ){
    if( ${$r_errdata}[0] =~ m/^(\d{3})\s/ ){  # 先頭が３桁の数字なら
      return int($1);
    }
  }
  return ERR__SYSTEM_ERROR;
}

#########################################################################################

sub get_result_msg
{
  my ($ip,$name,$result,$retry) = @_;

  if( $ip ne $name ){ $name = "$name ($ip)"; }

  if( $retry == 0 ){ $retry = ""; }
  else{ $retry = " (retryed)"; }

  my ($html_msg,$text_msg); # 戻り値

  if( $result == 0 ){ # 成功
    ++$ok_count;
    ++$get_count;
    my $msg = $str_SUCCEED;
    $html_msg = "<tr><td>$name</td><td> ---&gt; $msg$retry</td></tr>\n";
    $text_msg = "$name ---> $msg$retry\n";
  }
  elsif( $result == WARN__CLOCK_DIFF ){ # 機台の時計が合っていない
    ++$warn_count;
    ++$get_count;
    my $msg = $str_LOOM_CLOCK_IS_WRONG;
    if( $ip =~ m/^S/ ){  # スキャナーの場合
      $html_msg = "<tr><td>$name</td><td> ---&gt; <font color=blue>$msg$retry</font></td></tr>\n";
    }else{  # JAT710の場合
      $html_msg = "<tr><td><A HREF=http://$ip/ target=\"LoomWindow\">$name</A></td><td> ---&gt; <font color=blue>$msg$retry</font></td></tr>\n";
    }
    $text_msg = "$name ---> <font color=blue>$msg$retry</font>\n";
  }
  else{ # 電源OFF、エラー時
    my $msg = "";
    if(    $result == ERR__PING_TIMEOUT    ){ ++$poff_count; $msg = $str_POWER_OFF;    } # pingタイムアウト
    elsif( $result == ERR__PING_ERROR      ){ ++$err_count;  $msg = 'Network ERROR';   } # pingエラー
    elsif( $result == ERR__SOCKET_ERROR    ){ ++$err_count;  $msg = 'Socket ERROR';    }
    elsif( $result == ERR__HTTP_ERROR      ){ ++$err_count;  $msg = 'HTTP ERROR';      }
    elsif( $result == ERR__HTTP_NOT_FOUND  ){ ++$err_count;  $msg = 'HTTP ERROR (not found)'; }
    elsif( $result == ERR__NOT_SUPPORT     ){ ++$err_count;  $msg = 'Not Support TMS'; }
    elsif( $result == ERR__START_TIME_DIFF ){ ++$err_count;  $msg = 'Data ERROR (start_time diff)'; }
    elsif( $result == ERR__DATA_ERROR      ){ ++$err_count;  $msg = 'Data ERROR';      }
    else{                                     ++$err_count;  $msg = 'System ERROR';    } # システム関係のエラー

    $html_msg = "<tr><td>$name</td><td> ---&gt; <font color=red>$msg$retry</font></td></tr>\n";
    $text_msg = "$name ---> <font color=red>$msg$retry</font>\n";
  }

  return ($html_msg,$text_msg);
}

#########################################################################################
