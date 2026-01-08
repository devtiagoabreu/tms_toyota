package TMSDATAfinal;

###################################################################################################
#
# TMSDATAfinal.pm
#
###################################################################################################

use strict;
no strict "refs";	# for open($data_fd, "> $fname")
use DirHandle;
use Time::Local;
use File::Path;   # rmtree

use TMSstr;
use TMScommon;
use TMSselitem;
use TMSstophist;

###################################################################################################

my $debug_mode = 0;	# 中間ファイルを、消す。
#my $debug_mode = 1;	# 中間ファイルを、残す。

my $tmsdata_dir  = '..\\..\\tmsdata';

my $shift_dir     = "$tmsdata_dir\\shift";
my $shift_new_dir = "$shift_dir\\newdata";

my $shift_shift_dir = "$tmsdata_dir\\shift-shift";
my $shift_date_dir  = "$tmsdata_dir\\shift-date";
my $shift_week_dir  = "$tmsdata_dir\\shift-week";
my $shift_month_dir = "$tmsdata_dir\\shift-month";

my $operator_dir     = "$tmsdata_dir\\operator";
my $operator_new_dir = "$operator_dir\\newdata";

my $operator_date_dir  = "$tmsdata_dir\\operator-date";
my $operator_week_dir  = "$tmsdata_dir\\operator-week";
my $operator_month_dir = "$tmsdata_dir\\operator-month";

my @file_list = ();
my %shift_index = ();
my %date_index = ();
my %week_index = ();
my %month_index = ();

my $old_03_ym = 0;
my $old_06_ym = 0;
my $old_12_ym = 0;

my $data_fd = "FILE";		# &open_data_file() 用
my $data_fname = "";		#

###################################################################################################

sub make_final
{
  my ($phase) = @_;

  if( $debug_mode ){
    print "\n-- TMSDATAfinal::debug_mode = 1 --\n";
  }

  &TMScommon::make_dir($shift_shift_dir);
  &TMScommon::make_dir($shift_date_dir);
  &TMScommon::make_dir($shift_week_dir);
  &TMScommon::make_dir($shift_month_dir);

  &TMScommon::make_dir($operator_date_dir);
  &TMScommon::make_dir($operator_week_dir);
  &TMScommon::make_dir($operator_month_dir);

  &TMScommon::disp_percent(100,0, $phase); # 0%

  # シフトデータの作成 ------------------------------------------

  &make_shift_update_list();
  &make_shift_tmp_file();

  &TMScommon::disp_percent(100,20); # 20%

  &split_tmp_file( "shift", "shift", $shift_shift_dir, $old_03_ym );
  &split_tmp_file( "shift", "date",  $shift_date_dir,  $old_03_ym );

  &TMScommon::disp_percent(100,40); # 40%

  &split_tmp_file( "shift", "week",  $shift_week_dir,  $old_06_ym );
  &split_tmp_file( "shift", "month", $shift_month_dir, $old_12_ym );

  # オペレータデータの作成 --------------------------------------

  &make_operator_update_list();
  &make_operator_tmp_file();

  &TMScommon::disp_percent(100,60); # 60%

  &split_tmp_file( "operator", "date",  $operator_date_dir,  $old_03_ym );

  &TMScommon::disp_percent(100,80); # 80%

  &split_tmp_file( "operator", "week",  $operator_week_dir,  $old_06_ym );
  &split_tmp_file( "operator", "month", $operator_month_dir, $old_12_ym );

  # 停台履歴 ---------------------------------------------------
  &stophistory_mainte();

  &TMScommon::disp_percent(100,101); # 100% done

  # メモリー節約の為、配列のクリア ---------------------------------
  @file_list   = ();
  %shift_index = ();
  %date_index  = ();
  %week_index  = ();
  %month_index = ();
}

###################################################################################################
# week のデータのみ更新（週設定変更用）

sub make_week_final
{
  my ($phase) = @_;

  if( $debug_mode ){
    print "\n-- TMSDATAfinal::debug_mode = 1 --\n";
  }

  &TMScommon::make_dir($shift_week_dir);
  &TMScommon::make_dir($operator_week_dir);

  &TMScommon::disp_percent(100,0, $phase); # 0%

  # シフトデータの作成 ------------------------------------------

  &make_shift_update_list();
  &make_shift_week_tmp_file();

  &TMScommon::disp_percent(100,40); # 40%

  &split_tmp_file( "shift", "week", $shift_week_dir, $old_06_ym );

  # オペレータデータの作成 --------------------------------------

  &make_operator_update_list();
  &make_operator_week_tmp_file();

  &TMScommon::disp_percent(100,80); # 80%

  &split_tmp_file( "operator", "week", $operator_week_dir, $old_06_ym );

  &TMScommon::disp_percent(100,101); # 100% done

  # メモリー節約の為、配列のクリア ---------------------------------
  @file_list   = ();
  %shift_index = ();
  %date_index  = ();
  %week_index  = ();
  %month_index = ();
}

###################################################################################################
# 全データを再構築する要求（単に、????_update.txt を全ファイルにするだけ）

sub update_all_request
{
  # 古いデータを削除
  # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
  if( -d $shift_shift_dir    ){ system( "del /Q /F $shift_shift_dir\\*.*" );    }
  if( -d $shift_date_dir     ){ system( "del /Q /F $shift_date_dir\\*.*" );     }
  if( -d $shift_week_dir     ){ system( "del /Q /F $shift_week_dir\\*.*" );     }
  if( -d $shift_month_dir    ){ system( "del /Q /F $shift_month_dir\\*.*" );    }
  if( -d $operator_date_dir  ){ system( "del /Q /F $operator_date_dir\\*.*" );  }
  if( -d $operator_week_dir  ){ system( "del /Q /F $operator_week_dir\\*.*" );  }
  if( -d $operator_month_dir ){ system( "del /Q /F $operator_month_dir\\*.*" ); }
  &TMScommon::make_dir( $shift_new_dir );
  &TMScommon::make_dir( $operator_new_dir );

  if( open(LST,"> $shift_new_dir\\shift_update.txt") ){	# 更新ファイルのリストを取得する
    my $dir = new DirHandle $shift_dir;		# ディレクトリのファイルリストを取得する
    while( my $f = $dir->read ){
      if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.\d\.txt$/ ){ print LST $f."\n"; }
    }
    close(LST);
  }

  if( open(LST,"> $operator_new_dir\\operator_update.txt") ){	# 更新ファイルのリストを取得する
    my $dir = new DirHandle $operator_dir;		# ディレクトリのファイルリストを取得する
    while( my $f = $dir->read ){
      if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.txt$/ ){ print LST $f."\n"; }
    }
    close(LST);
  }

  ### 停止履歴の全てを更新処理の対象とする ###

  # 停止履歴フォルダ一覧の取得
  my ($stophist_dir, @stophist_subdir) = &TMSstophist::get_stophist_dir();

  if( open(LST,"> $stophist_dir\\history_update.txt") ){
    foreach( @stophist_subdir ){
      print LST "$_\n";
    }
    close(LST);
  }
  
}

# -------------------------------------------------------------------------------
# 週データを再構築する要求（単に、????_update.txt を全ファイルにするだけ）

sub update_week_request
{
  # 古いデータを削除
  if( -d $shift_week_dir     ){ system( "del /Q /F $shift_week_dir\\*.*" );     }
  if( -d $operator_week_dir  ){ system( "del /Q /F $operator_week_dir\\*.*" );  }
  &TMScommon::make_dir( $shift_new_dir );
  &TMScommon::make_dir( $operator_new_dir );

  if( open(LST,"> $shift_new_dir\\shift_update.txt") ){	# 更新ファイルのリストを取得する
    my $dir = new DirHandle $shift_dir;		# ディレクトリのファイルリストを取得する
    while( my $f = $dir->read ){
      if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.\d\.txt$/ ){ print LST $f."\n"; }
    }
    close(LST);
  }

  if( open(LST,"> $operator_new_dir\\operator_update.txt") ){	# 更新ファイルのリストを取得する
    my $dir = new DirHandle $operator_dir;		# ディレクトリのファイルリストを取得する
    while( my $f = $dir->read ){
      if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.txt$/ ){ print LST $f."\n"; }
    }
    close(LST);
  }

}

###################################################################################################

sub get_week
{
  my ($y,$m,$d) = @_;

  # 曜日を作る
  my $y_date = timelocal(0,0,0,$d,($m -1),($y -1900));
  my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($y_date);

  # その週の始まりを求める
  my $weekstart = &TMSselitem::get_value_of_week();
  my $offset = $wday - $weekstart;
  if( $offset < 0 ){ $offset += 7; }
  my $ws_date = ($y_date - ($offset*24*60*60));
  ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($ws_date);
  my $week_str = sprintf("%04d.%02d.%02d",($year +1900),($mon+1),$mday);

  return $week_str;
}

# -------------------------------------------------------------------------------

sub get_weekend_ym
{
  my ($fname) = @_;

  # 週の最終日の年月
  my @d = split(/\./,$fname);
  my $start = timelocal(0,0,0,$d[2],($d[1] -1),($d[0] -1900));
  my $end = ($start + (6*24*60*60));

  my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($end);
  my $ym = (($year +1900)*100) + ($mon+1);

  return $ym;
}

###################################################################################################
# 新たな取り込みにより更新の対象となるファイル名一覧の作成

sub make_shift_update_list
{
  @file_list   = ();	# 配列を初期化
  %shift_index = ();
  %date_index  = ();
  %week_index  = ();
  %month_index = ();
  $old_03_ym = 0;
  $old_06_ym = 0;
  $old_12_ym = 0;

  my %new_file = ();
  if( open(LST,"< $shift_new_dir\\shift_update.txt") ){	# 更新ファイルのリストを取得する
    while(<LST>){
      $_ =~ s/\n$//;		# 改行コードを削除。
      $new_file{$_} = 1;	# 連想配列に入れる
    }
    close(LST);

    my $dir = new DirHandle $shift_dir;		# ディレクトリのファイルリストを取得する
    while( my $f = $dir->read ){
      if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.\d\.txt$/ ){ push(@file_list,$f); }	# dirの結果を配列に入れる
    }

    if( $#file_list >= 0 ){
      @file_list = sort @file_list;
      my $new_ym = &TMScommon::get_ym_by_dot($file_list[$#file_list]);
      $old_03_ym = &TMScommon::get_old_ym($new_ym, 2);
      $old_06_ym = &TMScommon::get_old_ym($new_ym, 5);
      $old_12_ym = &TMScommon::get_old_ym($new_ym, 11);

      foreach(@file_list){
        if( exists( $new_file{$_} ) ){  # 今回更新されたものか？
          my @d = split(/\./);

          my $shift = "$d[0].$d[1].$d[2].$d[3]";
          my $date  = "$d[0].$d[1].$d[2]";
          my $week  = &get_week($d[0],$d[1],$d[2]);
          my $month = "$d[0].$d[1]";
          my $ym = (($d[0] *100) + $d[1]);

          if( $ym >= $old_03_ym ){ $shift_index{$shift} = 1; $date_index{$date} = 1; }
          if( $ym >= $old_06_ym ){ $week_index{$week}   = 1; }
          if( $ym >= $old_12_ym ){ $month_index{$month} = 1; }
        }
      }
    }
  }

  if( $debug_mode == 0 ){ unlink( "$shift_new_dir\\shift_update.txt" ); }

}

###################################################################################################
# 新規データを一つのファイルにまとめる。（後にシフト等ごとのファイルに分ける）

sub make_operator_update_list
{
  @file_list   = ();	# 配列を初期化
  %date_index  = ();
  %week_index  = ();
  %month_index = ();
  $old_03_ym = 0;
  $old_06_ym = 0;
  $old_12_ym = 0;

  my %new_file = ();
  if( open(LST,"< $operator_new_dir\\operator_update.txt") ){	# 更新ファイルのリストを取得する
    while(<LST>){
      $_ =~ s/\n$//;		# 改行コードを削除。
      $new_file{$_} = 1;	# 連想配列に入れる
    }
    close(LST);

    my $dir = new DirHandle $operator_dir;		# ディレクトリのファイルリストを取得する
    while( my $f = $dir->read ){
      if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.txt$/ ){ push(@file_list,$f); }	# dirの結果を配列に入れる
    }

    if( $#file_list >= 0 ){
      @file_list = sort @file_list;
      my $new_ym = &TMScommon::get_ym_by_dot($file_list[$#file_list]);
      $old_03_ym = &TMScommon::get_old_ym($new_ym, 2);
      $old_06_ym = &TMScommon::get_old_ym($new_ym, 5);
      $old_12_ym = &TMScommon::get_old_ym($new_ym, 11);

      foreach(@file_list){
        if( exists( $new_file{$_} ) ){
          my @d = split(/\./);

          my $date  = "$d[0].$d[1].$d[2]";
          my $week  = &get_week($d[0],$d[1],$d[2]);
          my $month = "$d[0].$d[1]";
          my $ym = (($d[0] *100) + $d[1]);

          if( $ym >= $old_03_ym ){ $date_index{$date}   = 1; }
          if( $ym >= $old_06_ym ){ $week_index{$week}   = 1; }
          if( $ym >= $old_12_ym ){ $month_index{$month} = 1; }
        }
      }
    }
  }

  if( $debug_mode == 0 ){ unlink( "$operator_new_dir\\operator_update.txt" ); }
}

###################################################################################################

sub make_shift_tmp_file
{
  my $run_tm = &TMSselitem::get_value_of_run_tm();
  my $effic  = &TMSselitem::get_value_of_effic();

  my $sc = 0;
  my $dc = 0;
  my $wc = 0;
  my $mc = 0;

  open(SFT,"> $shift_shift_dir\\shift.tmp" );
  open(DAY,"> $shift_date_dir\\date.tmp"   );
  open(WEK,"> $shift_week_dir\\week.tmp"   );
  open(MON,"> $shift_month_dir\\month.tmp" );

  foreach my $fname (@file_list){
    my @d = split(/\./,$fname);

    my $o = 0;
    my $s = 0;  my $shift = "$d[0].$d[1].$d[2].$d[3]";
    my $d = 0;  my $date  = "$d[0].$d[1].$d[2]";
    my $w = 0;  my $week  = &get_week($d[0],$d[1],$d[2]);
    my $m = 0;  my $month = "$d[0].$d[1]";

    if( exists($shift_index{$shift}) ){ $o = 1; $s = 1; }
    if( exists($date_index{$date})   ){ $o = 1; $d = 1; }
    if( exists($week_index{$week})   ){ $o = 1; $w = 1; }
    if( exists($month_index{$month}) ){ $o = 1; $m = 1; }

    if( $o ){
      open(IN,"< $shift_dir\\$fname");
      while(<IN>){
        my $data = &make_tmp_data(\$_, "shift", $run_tm, $effic);
        if( length($data) > 0 ){
          if( $s ){ print SFT "shift $shift,". $data; ++$sc; }
          if( $d ){ print DAY "date $date,".   $data; ++$dc; }
          if( $w ){ print WEK "week $week,".   $data; ++$wc; }
          if( $m ){ print MON "month $month,". $data; ++$mc; }
        }
      }
      close(IN);
    }
  }
  close(SFT);
  close(DAY);
  close(WEK);
  close(MON);

  if( $sc == 0 ){ unlink( "$shift_shift_dir\\shift.tmp"  ); }
  if( $dc == 0 ){ unlink( "$shift_date_dir\\date.tmp"    ); }
  if( $wc == 0 ){ unlink( "$shift_week_dir\\week.tmp"    ); }
  if( $mc == 0 ){ unlink( "$shift_month_dir\\month.tmp"  ); }
}

# --------------------------------------------------------------------------

sub make_shift_week_tmp_file
{
  my $run_tm = &TMSselitem::get_value_of_run_tm();
  my $effic  = &TMSselitem::get_value_of_effic();

  my $wc = 0;

  open(WEK,"> $shift_week_dir\\week.tmp"   );

  foreach my $fname (@file_list){
    my @d = split(/\./,$fname);
    my $w = 0;  my $week  = &get_week($d[0],$d[1],$d[2]);
    if( exists($week_index{$week}) ){ $w = 1; }

    if( $w ){
      open(IN,"< $shift_dir\\$fname");
      while(<IN>){
        my $data = &make_tmp_data(\$_, "shift", $run_tm, $effic);
        if( length($data) > 0 ){
          print WEK "week $week,". $data; ++$wc;
        }
      }
      close(IN);
    }
  }
  close(WEK);

  if( $wc == 0 ){ unlink( "$shift_week_dir\\week.tmp"    ); }
}

###################################################################################################

sub make_operator_tmp_file
{
  my $run_tm = &TMSselitem::get_value_of_run_tm();
  my $effic  = &TMSselitem::get_value_of_effic();

  my $dc = 0;
  my $wc = 0;
  my $mc = 0;

  open(DAY,"> $operator_date_dir\\date.tmp"   );
  open(WEK,"> $operator_week_dir\\week.tmp"   );
  open(MON,"> $operator_month_dir\\month.tmp" );

  foreach my $fname (@file_list){
    my @d = split(/\./,$fname);

    my $o = 0;
    my $d = 0;  my $date  = "$d[0].$d[1].$d[2]";
    my $w = 0;  my $week  = &get_week($d[0],$d[1],$d[2]);
    my $m = 0;  my $month = "$d[0].$d[1]";

    if( exists($date_index{$date})   ){ $o = 1; $d = 1; }
    if( exists($week_index{$week})   ){ $o = 1; $w = 1; }
    if( exists($month_index{$month}) ){ $o = 1; $m = 1; }

    if( $o ){
      open(IN,"< $operator_dir\\$fname");
      while(<IN>){
        my $data = &make_tmp_data(\$_, "operator", $run_tm, $effic);
        if( length($data) > 0 ){
          if( $d ){ print DAY "date $date,".   $data; ++$dc; }
          if( $w ){ print WEK "week $week,".   $data; ++$wc; }
          if( $m ){ print MON "month $month,". $data; ++$mc; }
        }
      }
      close(IN);
    }
  }
  close(DAY);
  close(WEK);
  close(MON);

  if( $dc == 0 ){ unlink( "$operator_date_dir\\date.tmp"   ); }
  if( $wc == 0 ){ unlink( "$operator_week_dir\\week.tmp"   ); }
  if( $mc == 0 ){ unlink( "$operator_month_dir\\month.tmp" ); }
}

# --------------------------------------------------------------------------

sub make_operator_week_tmp_file
{
  my $run_tm = &TMSselitem::get_value_of_run_tm();
  my $effic  = &TMSselitem::get_value_of_effic();

  my $wc = 0;

  open(WEK,"> $operator_week_dir\\week.tmp"   );

  foreach my $fname (@file_list){
    my @d = split(/\./,$fname);
    my $w = 0;  my $week  = &get_week($d[0],$d[1],$d[2]);
    if( exists($week_index{$week}) ){ $w = 1; }

    if( $w ){
      open(IN,"< $operator_dir\\$fname");
      while(<IN>){
        my $data = &make_tmp_data(\$_, "operator", $run_tm, $effic);
        if( length($data) > 0 ){
          print WEK "week $week,".$data; ++$wc;
        }
      }
      close(IN);
    }
  }
  close(WEK);

  if( $wc == 0 ){ unlink( "$operator_week_dir\\week.tmp" ); }
}

###################################################################################################
#
# 補足：常に、$data_fd eq "FILE" となるのは、バグ修正を少ない変更で行う為の暫定処置であり、
#       時間に余裕がある時に修正しても良い。 2009/12/09

sub open_data_file
{
  my ($fname) = @_;

  # 前回と同じなら、何もしない。
  if( $data_fname eq $fname ){ return $data_fd; }

  # 前回のファイルを閉じる
  &close_data_file();

  # 新しいファイルを開く
  if( open($data_fd, "> $fname") ){ $data_fname = $fname; }
  else{ $data_fname = ""; }

  return $data_fd;
}

# -------------------------------------------------------------------------

sub close_data_file
{
  if( $data_fname ne "" ){
    close($data_fd);
  }
  $data_fname = "";
}

###################################################################################################

sub split_tmp_file
{
  my ($mode, $index, $data_dir, $old_ym) = @_;

  my $tmpfile  = "$data_dir\\$index.tmp";
  my $sortfile = "$data_dir\\$index"."_sort.tmp";

  if( -f $sortfile ){ unlink($sortfile); }	# 古いソート済みファイルを消す

  if( -f $tmpfile ){
    # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
    system( "sort $tmpfile /O $sortfile" );	# データを合計できる様に、ソートする
    if( $debug_mode == 0 ){
      unlink( $tmpfile );	# 元ファイルを消す
    }
  }

  if( open(TMP,"< $sortfile") ){	# ソート済みファイルを処理する

    my $period   = "";
    my $mac_name = "";
    my $mac_type = "";  # LWT710対応
    my $ope_name = "";
    my $style    = "";
    my $beam     = "";
    my $ubeam    = "";
    my @seisan   = ();
    my @off_prod = ();   # スキャナオフ時の生産量 2006.1.12 追加
    my $run_tm   = 0;
    my $stop_ttm = 0;
    my @s_ct     = ();
    my @s_tm     = ();

    my $data = "";
    my $fd   = -1;

    while(<TMP>){  # １行目
      my $line = $_;

      &read_each_data(\$line,$mode,$index,\$period,\$mac_name,\$mac_type,\$ope_name,
                      \$style,\$beam,\$ubeam,\@seisan,\@off_prod,\$run_tm,\$stop_ttm,\@s_ct,\@s_tm);
      last;
    }
    while(<TMP>){  # ２行目以降
      my $line = $_;

      my $pd = "";
      my $mc = "";
      my $mt = "";  # LWT710対応(mac_type)
      my $op = "";
      my $sy = "";
      my $bm = "";
      my $ub = "";
      my @se = ();
      my @of = ();   # スキャナオフ時の生産量 2006.1.12 追加
      my $rt = 0;
      my $st = 0;
      my @ct = ();
      my @tm = ();

      &read_each_data(\$line,$mode,$index,\$pd,\$mc,\$mt,\$op,
                      \$sy,\$bm,\$ub,\@se,\@of,\$rt,\$st,\@ct,\@tm);

      # 同じデーターなら合計する
      if( ($period eq $pd) && ($mac_name eq $mc) && ($mac_type eq $mt) && ($ope_name eq $op)
          && ($style eq $sy) && ($beam eq $bm) && ($ubeam eq $ub) ){

        for( my $i=0; $i<=$#seisan; $i++ ){ $seisan[$i] += $se[$i]; $off_prod[$i] += $of[$i]; }
        $run_tm   += $rt;
        $stop_ttm += $st;
        for( my $i=0; $i<=$#s_ct; $i++ ){ $s_ct[$i] += $ct[$i]; }
        for( my $i=0; $i<=$#s_tm; $i++ ){ $s_tm[$i] += $tm[$i]; }
      }
      # 同じでなければ、前回までのデータを書き出す
      else{
        $data = &make_final_data($mode,$index,$period,$mac_name,$mac_type,$ope_name,
                                 $style,$beam,$ubeam,\@seisan,\@off_prod,$run_tm,$stop_ttm,\@s_ct,\@s_tm);
        $fd = &open_data_file( "$data_dir\\$period.txt" );
        print $fd $data;

	# さっき読み出したデータをコピー
	$period   = $pd;
        $mac_name = $mc;
        $mac_type = $mt;
        $ope_name = $op;
        $style    = $sy;
        $beam     = $bm;
        $ubeam    = $ub;
	@seisan   = @se;
	@off_prod = @of;
        $run_tm   = $rt;
        $stop_ttm = $st;
	@s_ct     = @ct;
	@s_tm     = @tm;
      }
    }
    $data = &make_final_data($mode,$index,$period,$mac_name,$mac_type,$ope_name,
                             $style,$beam,$ubeam,\@seisan,\@off_prod,$run_tm,$stop_ttm,\@s_ct,\@s_tm);
    $fd = &open_data_file( "$data_dir\\$period.txt" );
    print $fd $data;

    &close_data_file();
    close(TMP);

    if( $debug_mode == 0 ){ unlink( $sortfile ); }	# ソート済み中間ファイルを消す
  }

  # 古い既存データの削除 --------------------------------------

  my @files = ();
  my $dir = new DirHandle $data_dir;	# ディレクトリのファイルリストを取得する
  while( my $f = $dir->read ){
    if( $f =~ m/^\d{4}\.\d{2}\.[0-9\.]*txt$/ ){ push(@files,$f); }
  }
  $dir->close;
  @files = sort @files;
  foreach my $fname (@files){
    my $ym;
    if( $index eq "week" ){ $ym = &get_weekend_ym( $fname ); }	# 週の最終日の年月
    else{                   $ym = &TMScommon::get_ym_by_dot( $fname ); }

    if( $ym < $old_ym ){ unlink( "$data_dir\\$fname" ); }
    else{ last; }
  }

}

# -----------------------------------------------------------------------------------

sub read_each_data
{
  my ($r_line,$mode,$index,$r_pd,$r_mc,$r_mt,$r_op,
      $r_sy,$r_bm,$r_ub,$r_se,$r_of,$r_rt,$r_st,$r_ct,$r_tm) = @_;

  $$r_line =~ s/\n$//;	# 改行コードを削除。
  my @list = split(/,/,$$r_line);

  my %tmp = ();
  foreach(@list){
    my @data = split(/ /,$_,2);
    if( $#data >= 1 ){ $tmp{$data[0]} = $data[1]; }
  }

  $$r_pd = $tmp{$index};
  $$r_mc = $tmp{"mac_name"};
  $$r_mt = $tmp{"mac_type"};

  if( $mode eq "operator" ){ $$r_op = $tmp{"ope_name"}; }
  else{                      $$r_op = "dummy";          }

  $$r_sy = $tmp{"style"};
  $$r_bm = $tmp{"beam"};
  $$r_ub = $tmp{"ubeam"};
  @$r_se = split(/ /,$tmp{"seisan"});
  @$r_of = split(/ /,$tmp{"off_prod"});
  $$r_rt = $tmp{"run_tm"};
  $$r_st = $tmp{"stop_ttm"};
  @$r_ct = split(/ /,$tmp{"s_ct"});
  @$r_tm = split(/ /,$tmp{"s_tm"});
}


###################################################################################################
# 中間ファイル用出力
# 最低運転時間、最低稼働率を満たすデータのみ、１シフト１行で戻す

sub make_tmp_data
{
  my ($r_line, $mode, $min_run_tm, $min_effic) = @_;

  $$r_line =~ s/\n$//;	# 改行コードを削除。
# $$r_line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @list = split(/,/,$$r_line);

  my %tmp = ();
  foreach(@list){
    my @data = split(/ /,$_,2);
    if( $#data >= 1 ){ $tmp{$data[0]} = $data[1]; }
  }

  my $mac_name  = $tmp{"mac_name"};

  my $mac_type = "JAT";  # デフォルト(古いデータ用)
  if( exists($tmp{"mac_type"}) ){ $mac_type = $tmp{"mac_type"}; }

  my $ope_name  = "";
  if( $mode eq "operator" ){ $ope_name = $tmp{"ope_name"}; }

  my $style     = $tmp{"style"};
  my $beam      = $tmp{"beam"};
  my $ubeam     = $tmp{"ubeam"};
  my $seisan    = $tmp{"seisan"};

  my $off_prod  = "0 0 0 0";   # スキャナオフ時の生産量 2006.1.12 追加
  if( exists($tmp{"off_prod"}) ){ $off_prod = $tmp{"off_prod"}; }

  my $run_tm    = $tmp{"run_tm"};
  my $stop_ttm  = $tmp{"stop_ttm"};
  my $s_ct      = $tmp{"s_ct"};
  my $s_tm      = $tmp{"s_tm"};

  my $effic;
  if( ($run_tm + $stop_ttm) <= 0 ){ $effic = 0; }
  else{ $effic = ($run_tm * 100)/($run_tm + $stop_ttm); }

  if( $run_tm < ($min_run_tm * 60) ){ return ""; } # $rtは秒単位 $min_run_timeは分単位
  if( $effic  < $min_effic  ){ return ""; }

  #### Create Shift Data ####

  my $data = 	"mac_name ".	$mac_name.	",".
		"mac_type ".	$mac_type.	",";

  if( $mode eq "operator" ){
    $data .= 	"ope_name ".	$ope_name.	",";
  }

  $data .=	"style ".	$style.		",".
		"beam ".	$beam.		",".
		"ubeam ".	$ubeam.		",".
		"seisan ".	$seisan.	",".
		"off_prod ".	$off_prod.	",".
		"run_tm ".	$run_tm.	",".
		"stop_ttm ".	$stop_ttm.	",".
		"s_ct ".	$s_ct.		",".
		"s_tm ".	$s_tm.		"\n";

  return $data;
}

###################################################################################################
# 最終出力用

sub make_final_data
{
  my ($mode,$index,$period,$mac_name,$mac_type,$ope_name,
      $style,$beam,$ubeam,$r_seisan,$r_off_prod,$run_tm,$stop_ttm,$r_s_ct,$r_s_tm) = @_;

  my @stop_ct    = ();
  my @stop_tm    = ();
  my @wf1_ct     = ();
  my @wf1_tm     = ();
  my @wf2_ct     = ();
  my @wf2_tm     = ();
  my @lh_ct      = ();
  my @lh_tm      = ();

  $run_tm   = sprintf("%1.3f",($run_tm/60));
  $stop_ttm = sprintf("%1.3f",($stop_ttm/60));

  if( $mac_type eq "LWT" ){
    &TMScommon::get_detail_stop_lwt($r_s_ct, \@stop_ct, \@wf1_ct, \@wf2_ct, \@lh_ct);
    &TMScommon::get_detail_stop_lwt($r_s_tm, \@stop_tm, \@wf1_tm, \@wf2_tm, \@lh_tm);
  }else{  # JAT710
    &TMScommon::get_detail_stop_jat($r_s_ct, \@stop_ct, \@wf1_ct, \@wf2_ct, \@lh_ct);
    &TMScommon::get_detail_stop_jat($r_s_tm, \@stop_tm, \@wf1_tm, \@wf2_tm, \@lh_tm);
  }

  my $seisan = sprintf("%1.1f",($$r_seisan[0]/10));
  $seisan .= sprintf(" %1.1f",($$r_seisan[1]/10));
  $seisan .= sprintf(" %1.1f",($$r_seisan[2]/10));

  my $off_prod = sprintf("%1.1f",($$r_off_prod[0]/10));
  $off_prod .= sprintf(" %1.1f",($$r_off_prod[1]/10));
  $off_prod .= sprintf(" %1.1f",($$r_off_prod[2]/10));

  my $stop_ct = "";
  my $wf1_ct  = "";
  my $wf2_ct  = "";
  my $lh_ct   = "";
  for( my $i=0; $i<=$#stop_ct; $i++ ){ $stop_ct .= " ".$stop_ct[$i]; }
  for( my $i=0; $i<=$#wf1_ct;  $i++ ){ $wf1_ct  .= " ".$wf1_ct[$i];  }
  for( my $i=0; $i<=$#wf2_ct;  $i++ ){ $wf2_ct  .= " ".$wf2_ct[$i];  }
  for( my $i=0; $i<=$#lh_ct;   $i++ ){ $lh_ct   .= " ".$lh_ct[$i];   }

  my $stop_tm = "";
  my $wf1_tm  = "";
  my $wf2_tm  = "";
  my $lh_tm   = "";
  my $d;
  for( my $i=0; $i<=$#stop_tm; $i++ ){ $d=($stop_tm[$i]/60); if($d != 0){ $d=sprintf("%1.3f",$d); } $stop_tm .= " $d"; }
  for( my $i=0; $i<=$#wf1_tm;  $i++ ){ $d=($wf1_tm[$i]/60);  if($d != 0){ $d=sprintf("%1.3f",$d); } $wf1_tm  .= " $d"; }
  for( my $i=0; $i<=$#wf2_tm;  $i++ ){ $d=($wf2_tm[$i]/60);  if($d != 0){ $d=sprintf("%1.3f",$d); } $wf2_tm  .= " $d"; }
  for( my $i=0; $i<=$#lh_tm;   $i++ ){ $d=($lh_tm[$i]/60);   if($d != 0){ $d=sprintf("%1.3f",$d); } $lh_tm   .= " $d"; }

#  for( my $i=0; $i<=$#stop_tm; $i++ ){ $stop_tm .= sprintf(" %1.3f",($stop_tm[$i]/60)); }
#  for( my $i=0; $i<=$#wf1_tm;  $i++ ){ $wf1_tm  .= sprintf(" %1.3f",($wf1_tm[$i]/60));  }
#  for( my $i=0; $i<=$#wf2_tm;  $i++ ){ $wf2_tm  .= sprintf(" %1.3f",($wf2_tm[$i]/60));  }
#  for( my $i=0; $i<=$#lh_tm;   $i++ ){ $lh_tm   .= sprintf(" %1.3f",($lh_tm[$i]/60));   }


  #### Create Shift Data ####

  my $data = 	"$index ".	$period.	",".
	 	"mac_name ".	$mac_name.	",".
	 	"mac_type ".	$mac_type.	",";  # LWT710対応

  if( $mode eq "operator" ){
    $data .= 	"ope_name ".	$ope_name.	",";
  }

  $data .=	"style ".	$style.		",".
		"beam ".	$beam.		",".
		"ubeam ".	$ubeam.		",".
		"seisan ".	$seisan.	",".
		"off_prod ".	$off_prod.	",".   # スキャナオフ時の生産量 2006.1.12 追加
		"run_tm ".	$run_tm.	",".
		"stop_ttm ".	$stop_ttm.	",".

		"stop_ct".	$stop_ct.	",".
		"stop_tm".	$stop_tm.	",".
		"wf1_ct".	$wf1_ct.	",".
		"wf1_tm".	$wf1_tm.	",".
		"wf2_ct".	$wf2_ct.	",".
		"wf2_tm".	$wf2_tm.	",".
		"lh_ct".	$lh_ct.		",".
		"lh_tm".	$lh_tm.		"\n";

  return $data;
}

###################################################################################################
# 機能     停台履歴のうち最近の3ヶ月以外を削除する
# 引数   : なし
# 戻り値 : なし

sub rm_stophistory_3m
{
  # 停止履歴フォルダの一覧取得
  my ($stophist_dir, @stophist_subdir) = &TMSstophist::get_stophist_dir();

  # データフォルダが一つ以下なら削除不要
  if( $#stophist_subdir <= 0 ){ return; }

  # データ日で昇順に並び替え
  @stophist_subdir = sort @stophist_subdir; # yyyy.mm.dd

  # 最も新しい年月より3ヶ月前の年月を取得
  my $last_ym  = &TMScommon::get_ym_by_dot($stophist_subdir[$#stophist_subdir]);
  my $old3m_ym = &TMScommon::get_old_ym( $last_ym, 2 );

  # 3ヶ月前より古い年月のフォルダを削除
  foreach my $subdir ( @stophist_subdir ){
    my $ym = &TMScommon::get_ym_by_dot( $subdir );
    if( $ym < $old3m_ym ){ rmtree( "$stophist_dir\\$subdir", 0, 0 ); }
    else{ last; } # 古い順に並び替えられているのでそれ以降は削除不要
  }
}

###################################################################################################
# 機能  停台履歴のデータindexファイルを作成
# 引数   : なし
# 戻り値 : なし

sub stophistory_mainte
{
  ### 履歴元フォルダの所在パスの設定 ###
  my $stophist_dir = "$tmsdata_dir\\stop_history";

  # 再構築対象を history_update.txt から取得
  my @update_list = ();
  if( open(LST,"< $stophist_dir\\history_update.txt") ){
    while(<LST>){
      chomp;
      push(@update_list,$_);
    }
    close(LST);
  }
  if($#update_list < 0 ){ return; }

  # 最新3ヶ月より古い停止履歴フォルダを削除
  &rm_stophistory_3m();

  ### 停止履歴フォルダの保守を行う ###
  foreach( @update_list ){

    my $data_subdir = "$stophist_dir\\$_";
    if( ! -d $data_subdir ){ next; }

    my $dir = new DirHandle $data_subdir;
    my @file_list = $dir->read;
    $dir->close;

    ### 数字.txt以外のファイルを削除 ###
    my @fileno_list = ();
    foreach my $file ( @file_list ){
      if( ! -f "$data_subdir\\$file" ){ next; } # ファイル以外はスキップ

      if( $file !~ m/^\d+\.txt$/ ){
        # "数字.txt"の以外は削除
        unlink("$data_subdir\\$file");
      }
      else{  # "数字.txt"の場合
        my ($num, $sufix) = split(/\./,$file,2);
        push( @fileno_list, $num );
      }
    }

    ### データファイルのないフォルダは削除 ###
    if( $#fileno_list < 0 ){
      rmtree( $data_subdir, 0, 0 );
      next;
    }


    ### 同じ機台名の古い(番号の小さい)ファイルを削除 ###

    @fileno_list = sort {$b <=> $a} @fileno_list; # 逆順ソート

    my %index_data = ();
    foreach my $fileno ( @fileno_list ){

      if( open(HIST, "< $data_subdir\\$fileno.txt") ){
        my $line = <HIST>;  # １行目
        close(HIST);

        chomp $line; # 改行を除く
        my $fix      = "";
        my $mac_name = "";
        if( $line =~ m/^([^,]+)/          ){ $fix      = $1; }
        if( $line =~ m/,mac_name ([^,]+)/ ){ $mac_name = $1; } # 機台名

        if( ($fix eq "") or ($mac_name eq "") ){  # 不正なデータは削除
          unlink("$data_subdir\\$fileno.txt");
          next;
        }

        # 古いデータファイルを削除(配列の後ろが古いデータ)
        if( exists($index_data{$mac_name}) ){
          unlink("$data_subdir\\$fileno.txt");
          next;
        }

        # index用データを登録
        $index_data{$mac_name} = "$fix,$fileno.txt";
      }
    }

    ### indexファイルを作成 ###
    if( open(INDEX, "> $data_subdir\\index.txt") ){

      my @mac_name = sort {$a cmp $b} keys %index_data;
      foreach( @mac_name ){
        print INDEX $index_data{$_}.",$_\n";
      }
      close(INDEX);
    }
  }

}

###################################################################################################
1;
