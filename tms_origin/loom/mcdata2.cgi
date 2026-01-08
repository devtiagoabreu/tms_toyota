#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Time::Local;

use TMSstr;
use TMScommon;
use TMSdeny;
use TMSlock;
use TMSrestruct;
use TMSDATAnew;
use TMSDATAmerge;
use TMSDATAfinal;
use TMSDATAindex;

$| = 1;
require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_DATA_IMPORT_MEMCARD		= &TMSstr::get_str( "DATA_IMPORT_MEMCARD"	);
my $str_START_DATA_CHECKING		= &TMSstr::get_str( "START_DATA_CHECKING"	);
my $str_FUTURE_DATA 			= &TMSstr::get_str( "FUTURE_DATA" 		);
my $str_TOO_OLD_DATA			= &TMSstr::get_str( "TOO_OLD_DATA"		);
my $str_CANT_READ_FILE			= &TMSstr::get_str( "CANT_READ_FILE"		);
my $str_DATA_ERROR			= &TMSstr::get_str( "DATA_ERROR"		);
my $str_NOT_TMS_DATA			= &TMSstr::get_str( "NOT_TMS_DATA"		);
my $str_THERE_IS_NO_VALID_DATA		= &TMSstr::get_str( "THERE_IS_NO_VALID_DATA"	);
my $str_START_DATA_CONVERTING		= &TMSstr::get_str( "START_DATA_CONVERTING"	);
my $str_COMPLETED_ALL_PROPERLY		= &TMSstr::get_str( "COMPLETED_ALL_PROPERLY"	);


if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

my $html = new CGI;

my @file_list = $html->param('file');
if( $#file_list < 0 ){
  print &TMScommon::no_data_page( $menu_color, $body_color );
  exit;
}


my $lockfile = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::create_lockfile($lockfile,$ENV{REMOTE_ADDR},1,60,\$other_user) ){	# 同時使用を禁止（レベル１）
  print &TMSlock::data_updating_page( $other_user );
  exit;
}


my $datadir = $html->param('datadir');
#if( open(FILE,"> datadir.txt") ){ # change 2008.3.18
#  print FILE "$datadir";
#  close(FILE);
#}

# リダイレクトページの表示

my $title = $str_DATA_IMPORT_MEMCARD;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function move_next_page() {\n".
	"    location.href = \"mcdata3.cgi\";\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=$body_color OnLoad=\"setTimeout('move_next_page()',2000)\">\n".
	"<pre>\n";

&TMScommon::make_dir( '../../tmsdata' );
&TMScommon::make_dir( '../../tmsdata/loom' );

# (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
system( 'del /Q /F ..\..\tmsdata\loom\*.*' );

#------------------------------------------------------------------------------------
# データファイルの内容チェック

use constant WARN_FUTURE_DATA  => 1;
use constant WARN_TOO_OLD_DATA => 2;
use constant ERR_CANT_OPEN     => 3;
use constant ERR_NOT_SUPPORT   => 4;
use constant ERR_DIFF_TIME     => 5;
use constant ERR_DATA_ERROR    => 6;

# ログ用
my $ok_count   = 0;	# データ収集成功機台数
my $warn_count = 0;	# 時刻ずれ機台数
my $err_count  = 0;	# エラー機台数

open(DATA,'> mcdata3.dat');
print "**** $str_START_DATA_CHECKING ****\n";

my $okcount = 0;
my $msg;
foreach my $fullname (@file_list){
  my @fn = split( /\\/,$fullname );	# \で区切って、ファイル名だけ取り出す
  my $fname = $fn[$#fn];

  my $result = &mcdata_check($fullname, $fname);

  if( $result == ERR_DATA_ERROR ){		# 通常のメモリーカードデータ？
    if( -f "..\\setting\\service.txt" ){	# サービス員用ＴＭＳの場合
      $result = &service_mcdata_check($fullname, $fname);
    }
  }

  if(    $result == 0                 ){ ++$ok_count;   $msg = "OK"; ++$okcount; }
  elsif( $result == WARN_FUTURE_DATA  ){ ++$warn_count; $msg = "<font color=blue>$str_FUTURE_DATA</font>";  ++$okcount; }
  elsif( $result == WARN_TOO_OLD_DATA ){ ++$warn_count; $msg = "<font color=blue>$str_TOO_OLD_DATA</font>"; ++$okcount; }
  elsif( $result == ERR_CANT_OPEN     ){ ++$err_count;  $msg = "<font color=red>$str_CANT_READ_FILE</font>"; }
  elsif( $result == ERR_NOT_SUPPORT   ){ ++$err_count;  $msg = "<font color=red>Not Support TMS</font>";     }
  elsif( $result == ERR_DIFF_TIME     ){ ++$err_count;  $msg = "<font color=red>$str_DATA_ERROR</font>";     }
  else                                 { ++$err_count;  $msg = "<font color=red>$str_NOT_TMS_DATA</font>";   }

  print DATA "<tr><td>$fname</td><td> ---&gt; $msg</td></tr>\n";
  print "$fname ---> $msg\n";

}

# データ収集結果をログファイルに残す
&TMScommon::log_entry( "Get MemCard TMS Data (OK=$ok_count WARN=$warn_count ERR=$err_count)" );

#------------------------------------------------------------------------------------
# 有効なデータが無い場合

if( $okcount == 0 ){
  $msg = $str_THERE_IS_NO_VALID_DATA;
  print DATA "<tr><td colspan=2 align=center><font color=red><B>*** $msg ****</B></font></td></tr>\n";
  print "<font color=red>**** $msg ****</font>\n";
}

#------------------------------------------------------------------------------------
# データの処理

else{
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

  $msg = $str_COMPLETED_ALL_PROPERLY;
  print DATA "<tr><td colspan=2 align=center><B>*** $msg ****</B></td></tr>\n";
  print "**** $msg ****\n";

  # データ処理終了のログ
  &TMScommon::log_entry( "End Data Convert" );
}

close(DATA);

print	"</pre>\n".
	"</body></html>\n";

unlink($lockfile);	# ロックファイルを削除

exit;

################################################################################

sub mcdata_check
{
  my ($fullname, $fname) = @_;

  my $hi_st_tm = "";
  my $sh_st_tm = "";
  my $op_st_tm = "";

  my $history_ari = 0;
  my @data = ();

  my $err = 0;
  if( open( SRC, "< $fullname" ) ){

    my $sh_flg = 0;
    my $op_flg = 0;
    my $ns_flg = 0;
    while(<SRC>){	# データ先頭部分 読み込み
      if(    m/^history_start_time /  ){ $hi_st_tm = $_; $history_ari = 1; } # add 2005.6.7
      elsif( m/^shift_start_time /    ){ $sh_st_tm = $_; $sh_flg = 1; }
      elsif( m/^operator_start_time / ){ $op_st_tm = $_; $op_flg = 1; }
      elsif( m/^Not supported\./      ){ $ns_flg = 1; last; }

      if( $sh_flg && $op_flg ){ last; }  # 古い機台に対応する為、$hi_flg は見ない
    }

    if( $sh_flg && $op_flg ){
      @data = <SRC>;	# 残りのデータ 読み込み
      if( $#data < 4 ){ $err = ERR_DATA_ERROR; }
    }
    elsif( $ns_flg == 1 ){ $err = ERR_NOT_SUPPORT; }
    else{ $err = ERR_DATA_ERROR; }

    close(SRC);
    if( $err ){ return $err; }
  }
  else{ return ERR_CANT_OPEN; }

  # ------------------------------------------------------------------------------
  # データ先頭と末尾の start_time を比較

  if( $history_ari ){  # 停止履歴ある場合（ add 2005.6.7 ）
    my $hi_flg = 0;
    my $sh_flg = 0;
    my $op_flg = 0;
    for( my $i=($#data-3); $i<=$#data; $i++ ){
      my $line = $data[$i];
      if(    $line =~ m/^history_start_time /  ){ if( $line eq $hi_st_tm ){ $hi_flg = 1; } }
      elsif( $line =~ m/^shift_start_time /    ){ if( $line eq $sh_st_tm ){ $sh_flg = 1; } }
      elsif( $line =~ m/^operator_start_time / ){ if( $line eq $op_st_tm ){ $op_flg = 1; } }
    }
    if( ($hi_flg == 0) || ($sh_flg == 0) || ($op_flg == 0) ){ return ERR_DIFF_TIME; }
  }
  else{  # 停止履歴無い場合（古い機台）
    my $sh_flg = 0;
    my $op_flg = 0;
    for( my $i=($#data-2); $i<=$#data; $i++ ){
      my $line = $data[$i];
      if(    $line =~ m/^shift_start_time /    ){ if( $line eq $sh_st_tm ){ $sh_flg = 1; } }
      elsif( $line =~ m/^operator_start_time / ){ if( $line eq $op_st_tm ){ $op_flg = 1; } }
    }
    if( ($sh_flg == 0) || ($op_flg == 0) ){ return ERR_DIFF_TIME; }
  }

  # ------------------------------------------------------------------------------
  # sys_time の行を読み出し → get_timeにする。

  my $sys_time = "";
  my $get_time = "";
  for( my $i=0; $i<=$#data; $i++ ){
    my $line = $data[$i];
    if( $line =~ m/^sys_time / ){ $sys_time = $line; last; }
    if( $line =~ m/^#end_of_data/ ){ return ERR_DATA_ERROR; }
  }
  if( length($sys_time) <= 0 ){ return ERR_DATA_ERROR; }
  else{
    $get_time = $sys_time;
    $get_time =~ s/sys_time/get_time/;
  }

  # ------------------------------------------------------------------------------
  # データをファイルに保存

  $fname =~ s/\s/_/g;		# スペースはアンダーバーに変換。
  $fname =~ s/\.txt$//;

  my $end_line;
  if( $history_ari ){ $end_line = $#data-3; }  # 停止履歴ある場合（ add 2005.6.7 ）
  else{               $end_line = $#data-2; }  # 停止履歴無い場合（古い機台）

  open(FILE,"> ../../tmsdata/loom/$fname.txt");
  print FILE "$get_time";
  for(my $i=0; $i<=$end_line; $i++ ){ print FILE $data[$i]; }
  close(FILE);

  # ------------------------------------------------------------------------------
  # 機台の時計とPCの時計を比較

  my $pc_date = time();
  $sys_time =~ s/\n$//;		# 改行コードを削除。
  $sys_time =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @d = split(/ /,$sys_time);
  my $sys_date = timelocal($d[7],$d[6],$d[5],$d[3],($d[2] -1),($d[1] -1900));
  my $diff = $sys_date - $pc_date;
  if( $diff > 600          ){ return WARN_FUTURE_DATA;  }
  if( $diff < -(7*24*3600) ){ return WARN_TOO_OLD_DATA; }

  return 0;
}

################################################################################
#
# 通常のメモリーカードデータを読み込む（サービス員用ＴＭＳ）
#
# 読み込む対象は、モニター(必須)と、シフトスケジュール(無くても可)

sub service_mcdata_check
{
  my ($fullname, $fname) = @_;

  my @monitor = ();
  my @shift = ();
  my @MJ_t_tm = ("0","0","0","0","0");
  my @MJ_t_rt = ("0","0","0","0","0");
  my @MJ_t_st = ("0","0","0","0","0");
  my $sys_time = "";
  my $mac_type = "JAT";

  if( open( SRC, "< $fullname" ) ){

    my $data_kind = -1;
    while(<SRC>){
      my $line = $_;
      # JAT
      if(    $line =~ m/^JAT700-MCARD-DATA moni_monitor / ){ $data_kind = 2; }	# データの始まり
      elsif( $line =~ m/^JAT700-MCARD-DATA shift /        ){ $data_kind = 3; }
      # LWT
      elsif( $line =~ m/^LW700-MCARD-DATA moni_monitor /  ){ $data_kind = 2; $mac_type = "LWT"; }
      elsif( $line =~ m/^LW700-MCARD-DATA shift /         ){ $data_kind = 3; $mac_type = "LWT"; }

      # モニターデータ
      if( $data_kind == 2 ){
        push(@monitor,$line);
        if(    $line =~ m/^MJ_t_s([0-4])_tm (.+)/ ){ $MJ_t_tm[$1] = $2; }	# 現在シフトを調べる為
        elsif( $line =~ m/^MJ_t_s([0-4])_rt (.+)/ ){ $MJ_t_rt[$1] = $2; }	#     〃
        elsif( $line =~ m/^MJ_t_s([0-4])_st (.+)/ ){ $MJ_t_st[$1] = $2; }	#     〃
        elsif( $line =~ m/^PM_i_ctime /  ){ $sys_time = $line;    }	# データ生成時刻
      }
      # シフトデータ
      elsif( $data_kind == 3 ){
        push(@shift,$line);
      }
      # データの終わり
      if( $line =~ m/^\#end_of_data/ ){ $data_kind = -1; }
    }
    close(SRC);
  }

  if( $#monitor < 2 ){ return ERR_DATA_ERROR; }
  if( $#MJ_t_tm < 4 ){ return ERR_DATA_ERROR; }
  if( length($sys_time) == 0 ){ return ERR_DATA_ERROR; }

  # ------------------------------------------------------------------------------
  # 現在シフトを開始時刻を調べる

  my $now_shift = -1;

  for( my $i=0; $i<=4; $i++ ){

    $MJ_t_tm[$i] =~ s/^\s+//;	# 念の為、先頭のスペースを削除。
    if( $MJ_t_tm[$i] =~ m/^[1-9]/ ){  # 開始時刻が登録されている

      $MJ_t_rt[$i] =~ s/\s//g;  # 念の為、スペースを削除

      $MJ_t_st[$i] =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
      $MJ_t_st[$i] =~ s/\s$//;	# 念の為、行末のスペースを削除。
      $MJ_t_st[$i] =~ s/^\s//;	# 念の為、先頭のスペースを削除。
      my @st = split(/ /,$MJ_t_st[$i]);

      # 運転＋停止時間の計算
      my $rst = $MJ_t_rt[$i];
      foreach(@st){ $rst += $_; }

      # 運転停止時間が0でなければ
      if( $rst > 0 ){ $now_shift = $i; }
    }
  }

  if( $now_shift == -1 ){ return ERR_DATA_ERROR; }

  # ------------------------------------------------------------------------------
  # ファイル名のチェック

  $fname =~ s/\s/_/g;		# スペースはアンダーバーに変換。
  $fname =~ s/\.txt$//;

  my $mac_name = $fname;	# 機台名は、ファイル名から作成
  $mac_name =~ s/\.([^\.]+)$//;	# 拡張子を削除

  # ------------------------------------------------------------------------------
  # データをファイルに保存

  open(FILE,"> ../../tmsdata/loom/$fname.txt");

  # カレントデータ(最低限の必要分)
  if( $mac_type eq "JAT" ){
    print FILE	"JAT710-TMS-DATA current -----------\n";
  }else{
    print FILE	"LW700-TMS-DATA current -----------\n";
  }
  print FILE	"ip_addr $mac_name\n".			# IPアドレスは、機台名
		"mac_name $mac_name\n".
		"shift $now_shift\n".
		"#end_of_data\n";

  # モニターデータ
  foreach(@monitor){ print FILE $_; }

  # シフトスケジュール
  if( $#shift >= 2 ){
    foreach(@shift){ print FILE $_; }
  }

  close(FILE);

  # ------------------------------------------------------------------------------
  # 機台の時計とPCの時計を比較

  my $pc_date = time();
  $sys_time =~ s/\n$//;		# 改行コードを削除。
  $sys_time =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @d = split(/ /,$sys_time);
  my $sys_date = timelocal($d[7],$d[6],$d[5],$d[3],($d[2] -1),($d[1] -1900));
  my $diff = $sys_date - $pc_date;
  if( $diff > 600          ){ return WARN_FUTURE_DATA;  }
  if( $diff < -(7*24*3600) ){ return WARN_TOO_OLD_DATA; }

  return 0;
}

################################################################################
