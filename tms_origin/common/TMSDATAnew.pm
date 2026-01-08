package TMSDATAnew;

###################################################################################################
#
# TMSDATAnew.pm
#
###################################################################################################

use strict;
use DirHandle;

use TMSstr;
use TMScommon;

###################################################################################################

my $tmsdata_dir  = "..\\..\\tmsdata";

my $loom_dir     = "$tmsdata_dir\\loom";
my $current_dir  = "$tmsdata_dir\\current";
my $shift_dir    = "$tmsdata_dir\\shift";
my $operator_dir = "$tmsdata_dir\\operator";
my $history_dir  = "$tmsdata_dir\\stop_history";

my $current_new_dir  = "$current_dir\\newdata";
my $shift_new_dir    = "$shift_dir\\newdata";
my $operator_new_dir = "$operator_dir\\newdata";

my %shift_fix_file = ();	# key: fix情報を読み込み済みデータファイル名, val: 1
my %shift_fix_data = ();	# key: fix情報, val: 1
my %operator_fix_file = ();
my %operator_fix_data = ();
my %history_fix_file = ();
my %history_fix_data = ();

my $mac_type;		# JAT710 or LWT710
my $hist_mac_type;	# JAT710 or LWT710
my %current = ();	# データ用連想配列
my %shift = ();
my %operator = ();
my %schedule = ();
my @ope_name_list = ();
my @history_t  = ();
my @history_d0 = ();
my @history_d1 = ();
my $history_t_day  = "";
my $history_d0_day = "";
my $history_d1_day = "";

my $current_count;		# 新規データ数
my $shift_count;
my $operator_count;

my @shift_update_list = ();	# 今回更新されたデータファイル名のリスト
my @operator_update_list = ();
my @history_update_list = ();

my $tomorrow = &get_tomorrow_daynum();	# 明日の日付

###################################################################################################

sub make_newdata
{
  my ($phase) = @_;

  &TMScommon::make_dir( $tmsdata_dir );
  &TMScommon::make_dir( $current_dir );
  &TMScommon::make_dir( $current_new_dir );
  &TMScommon::make_dir( $shift_dir );
  &TMScommon::make_dir( $shift_new_dir );
  &TMScommon::make_dir( $operator_dir );
  &TMScommon::make_dir( $operator_new_dir );
  &TMScommon::make_dir( $history_dir );

  # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
  system( 'del /Q /F ..\..\tmsdata\shift\newdata\*.*' );
  system( 'del /Q /F ..\..\tmsdata\operator\newdata\*.*' );
  unlink( "$history_dir\\history_update.txt" );

  my @file = ();
  my $dir = new DirHandle $loom_dir;		# ディレクトリのファイルリストを取得する
  while( my $f = $dir->read ){
    if( $f =~ m/\.txt$/ ){ push(@file,$f); }	# dirの結果を配列に入れる
  }
  $dir->close;
  @file = sort @file;		# 配列をソートする。

  ### 経過表示 ###
  my $total = ($#file + 1);
  my $count = 0;
  &TMScommon::disp_percent($total, $count, $phase);  # 経過表示（開始）

  &open_current_new_file();
  &open_shift_new_file();
  &open_operator_new_file();

  for( my $i=0; $i<=$#file; $i++ ){

    &init_ope_name_list();	# サービス員用ＴＭＳ対応
    my $data_kind = 0;		# 先頭行 get_time 用

    $mac_type      = "JAT";		# 機台種類のデフォルト
    $hist_mac_type = "JAT710";		# 機台種類のデフォルト

    open(IN,"< $loom_dir\\$file[$i]");
    while(<IN>){
      my $line = $_;

      #### 余分なスペース、改行の削除 ####
      $line =~ s/\n$//;		# 改行コードを削除。
      $line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
      $line =~ s/\s$//;		# 行端のスペースを削除。

      #### データセクションの区別 ####
      if( $line =~ m/^JAT7/ ){
        if(    $line =~ m/^JAT710-TMS-DATA current /        ){ $data_kind = 1; next; }
        elsif( $line =~ m/^JAT700-MCARD-DATA moni_monitor / ){ $data_kind = 2; next; }
        elsif( $line =~ m/^JAT700-MCARD-DATA shift /        ){ $data_kind = 3; next; }
        elsif( $line =~ m/^JAT710-TMS-DATA stop_history /   ){ $data_kind = 4; next; }
      }
      elsif( $line =~ m/^LW7/ ){
        if(    $line =~ m/^LW700-TMS-DATA current /        ){ $data_kind = 1; $mac_type = "LWT"; next; }
        elsif( $line =~ m/^LW700-MCARD-DATA moni_monitor / ){ $data_kind = 2; $mac_type = "LWT"; next; }
        elsif( $line =~ m/^LW700-MCARD-DATA shift /        ){ $data_kind = 3; $mac_type = "LWT"; next; }
        elsif( $line =~ m/^LW700-TMS-DATA stop_history /   ){ $data_kind = 4; $hist_mac_type = "LWT710"; next; }
      }
      elsif( $line =~ m/^\#end_of_data/ ){ $data_kind = -1; next; }
      if( $data_kind == -1){ next; }

      #### データの加工 ####
      my @data = split(/ /,$line,2);

      if( $#data == 0 ){		# 見出しだけで、データが無い場合
        if( ($data[0] eq 'mac_name') ||
            ($data[0] =~ m/style/)   ||
            ($data[0] =~ m/beam/)    ||
            ($data[0] =~ m/ubeam/)   ||
            ($data[0] =~ m/_sn$/)    ||
            ($data[0] =~ m/_bn_t$/)  ||
            ($data[0] =~ m/_bn_b$/) ){ $data[1] = 'Undefined'; }
        else{ $data[1] = ''; }
      }

      if( $data[0] =~ m/^NAME$/ ){	# NAME の 最初と最後の " を削除
        my @name = split(/ /,$data[1],2);
        $name[1] =~ s/^"//;
        $name[1] =~ s/"$//;
        $data[1] = "$name[0] $name[1]";
      }

      $data[1] =~ s/"/_/g;		# " はアンダーバーに変換。
      $data[1] =~ s/,/_/g;		# , はアンダーバーに変換。

      #### データ取り込み ####
      if( $data_kind == 0 ){	# 先頭行
        if( $data[0] eq 'get_time' ){ $current{$data[0]} = $data[1]; }
	$data_kind = -1;
      }
      elsif( $data_kind == 1 ){	# JAT710-TMS-DATA current
        $current{$data[0]} = $data[1];
      }
      elsif( $data_kind == 2 ){	# JAT700-MCARD-DATA moni_monitor
        if(    $data[0] =~ m/^MJ_/ ){ $shift{$data[0]}    = $data[1]; }
        elsif( $data[0] =~ m/^PM_/ ){ $operator{$data[0]} = $data[1]; }
      }
      elsif( $data_kind == 3 ){	# JAT700-MCARD-DATA shift
        &set_schedule(\$data[0],\$data[1]);
      }
      elsif( $data_kind == 4 ){	# JAT710-TMS-DATA stop_history
        &set_history(\$data[0],\$data[1]);
      }

    }
    close(IN);

    if( exists($current{'mac_name'}) ){	# 機台名のデータがある場合のみ処理する

      # 機台名が未定義の場合、ip_addr を機台名にする。
      if( $current{'mac_name'} eq 'Undefined' ){ $current{'mac_name'} = $current{'ip_addr'}; }

      if( exists($current{'sys_time'}) ){ &write_current(); }	# サービス員用ＴＭＳ対応
      &write_shift();
      &write_operator();
      &write_history();
    }

    %current = ();		# データ用連想配列のクリア
    %shift = ();
    %operator = ();
    %schedule = ();
    @ope_name_list = ();
    @history_t  = ();
    @history_d0  = ();
    @history_d1  = ();
    $history_t_day  = "";
    $history_d0_day = "";
    $history_d1_day = "";

    &TMScommon::disp_percent($total, ++$count);  # 経過表示（途中）
  }

  &close_current_new_file();
  &close_shift_new_file();
  &close_operator_new_file();

  &write_update_list();
  &TMScommon::disp_percent(100,101);  # 経過表示（終了）


  # メモリー節約の為、配列のクリア ---------------------------------
  %shift_fix_file    = ();
  %shift_fix_data    = ();
  %operator_fix_file = ();
  %operator_fix_data = ();
  %history_fix_file = ();
  %history_fix_data = ();
  @shift_update_list    = ();
  @operator_update_list = ();
  @history_update_list = ();

}

################################################################################

sub get_tomorrow_daynum
{
  my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime(time + (24*3600));	# 明日の日付
  my $dnum = ((($year+1900) *10000) + (($mon+1) *100) + $mday);

  return $dnum;
}

# -------------------------------------------------------------------------------

sub get_daynum_by_dot		# shiftname, day
{
  my( $day ) = @_;

  my @d = split(/\./,$day);
  my $dnum = (($d[0] *10000) + ($d[1] *100) + $d[2]);
  return $dnum;
}

# -------------------------------------------------------------------------------

sub get_daynum_by_space		# sys_time
{
  my( $day ) = @_;

  my @d = split(/ /,$day);
  my $dnum = (($d[0] *10000) + ($d[1] *100) + $d[2]);
  return $dnum;
}

################################################################################

sub init_ope_name_list		# サービス員用ＴＭＳ対応
{
  $ope_name_list[0] = 'Undefined1';
  $ope_name_list[1] = 'Undefined2';
  $ope_name_list[2] = 'Undefined3';
  $ope_name_list[3] = 'Undefined4';
  $ope_name_list[4] = 'Undefined5';
  $ope_name_list[5] = 'Undefined6';
}

# -------------------------------------------------------------------------------

sub set_schedule
{
  my ($r_key,$r_val) = @_;

  if($$r_key eq 'NAME'){
    my @data = split(/ /,$$r_val,2);
    if( $data[1] eq '' ){ my $n = $data[0]+1; $data[1] = "Undefined$n"; }
    $ope_name_list[$data[0]] = $data[1];
    $schedule{'NAME_'.$data[0]} = $data[1];
  }
  elsif($$r_key eq 'DAY'){
    my @data = split(/ /,$$r_val,2);
    $schedule{'DAY_'.$data[0]} = $data[1];
  }
  else{
    $schedule{$$r_key} = $$r_val;
  }
}

################################################################################

sub check_shift_fix
{
  my ($shiftname, $mac_name) = @_;

  my $daynum = &get_daynum_by_dot($shiftname);
  if( $daynum > $tomorrow ){ return 1; }	# 明日より未来は取り込まない

  my $fname = "$shiftname.txt";
  unless( exists($shift_fix_file{$fname}) ){
    $shift_fix_file{$fname} = 1;

    if( open(DAT,"< $shift_dir\\$fname") ){
      while(<DAT>){
        if( m/^fixed,/ ){
          if( m/,mac_name ([^,]+)/ ){
            $shift_fix_data{"$shiftname $1"} = 1;
          }
        }
      }
      close(DAT);
    }
  }

  if( exists( $shift_fix_data{"$shiftname $mac_name"} ) ){ return 1; }	# fixed
  return 0;
}

# -------------------------------------------------------------------------------

sub check_operator_fix
{
  my ($day, $mac_name, $ope_num) = @_;

  my $daynum = &get_daynum_by_dot($day);
  if( $daynum > $tomorrow ){ return 1; }	# 明日より未来は取り込まない

  my $fname = "$day.txt";
  unless( exists($operator_fix_file{$fname}) ){
    $operator_fix_file{$fname} = 1;

    if( open(DAT,"< $operator_dir\\$fname") ){
      while(<DAT>){
        if( m/^fixed,/ ){
          if( m/,mac_name ([^,]+)/ ){
            my $m = $1;
            if( m/,ope_num ([^,]+)/ ){
              my $o = $1;
              $operator_fix_data{"$day $m $o"} = 1;
            }
          }
        }
      }
      close(DAT);
    }
  }

  if( exists( $operator_fix_data{"$day $mac_name $ope_num"} ) ){ return 1; }	# fixed
  return 0;
}

# -------------------------------------------------------------------------------

sub check_history_fix
{
  my ($day, $mac_name) = @_;

  my $daynum = &get_daynum_by_dot($day);
  if( $daynum > $tomorrow ){ return 1; }	# 明日より未来は取り込まない

  unless( exists($history_fix_file{$day}) ){
    $history_fix_file{$day} = 1;

    &TMScommon::make_dir("$history_dir\\$day");  # 日付のフォルダが無ければ、作る

    if( open(DAT,"< $history_dir\\$day\\index.txt") ){
      while(<DAT>){
        if( m/^fixed,/ ){
          $_ =~ s/\n$//;		# 改行コードを削除。
          my @d = split(/,/,$_,3);	# "fixed,file_name,mac_name"
          $history_fix_data{"$day $d[2]"} = 1;
        }
      }
      close(DAT);
    }
  }

  if( exists( $history_fix_data{"$day $mac_name"} ) ){ return 1; }	# fixed
  return 0;
}

################################################################################

sub write_update_list
{

  if( $#shift_update_list >= 0 ){
    @shift_update_list = sort @shift_update_list;

    open(LST,"> $shift_new_dir\\shift_update.txt");
    foreach(@shift_update_list){
      print LST $_."\n";
    }
    close(LST);
  }


  if( $#operator_update_list >= 0 ){
    @operator_update_list = sort @operator_update_list;

    open(LST,"> $operator_new_dir\\operator_update.txt");
    foreach(@operator_update_list){
      print LST $_."\n";
    }
    close(LST);
  }


  if( $#history_update_list >= 0 ){
    @history_update_list = sort @history_update_list;

    open(LST,"> $history_dir\\history_update.txt");
    foreach(@history_update_list){
      print LST $_."\n";
    }
    close(LST);
  }

}


################################################################################

sub open_current_new_file
{
  $current_count = 0;
  open(CUR,"> $current_new_dir\\current.txt");
  open(SET,"> $current_new_dir\\setting.txt");
}

# -------------------------------------------------------------------------------

sub close_current_new_file
{
  close(CUR);
  close(SET);

  if( $current_count == 0 ){
    unlink( "$current_new_dir\\current.txt" );
    unlink( "$current_new_dir\\setting.txt" );
  }
}

# -------------------------------------------------------------------------------

sub write_current
{
  my $sys_time = $current{'sys_time'};

  my $daynum = &get_daynum_by_space($sys_time);
  if( $daynum > $tomorrow ){ return; }		# 明日より未来は取り込まない

  my $mac_name = $current{'mac_name'};
  my $ip_addr  = $current{'ip_addr'};
  my $get_time = $current{'get_time'};

  my @d = split(/ /,$shift{MJ_t_s0_tm});
  my $shiftname = sprintf("%04d.%02d.%02d.%d",$d[0],$d[1],$d[2],$current{shift});

  my $ubeam   = $current{'ubeam'};
  my $s_ubeam = $current{'s_ubeam'};
  my $r_ubeam = $current{'r_ubeam'};
  if( $current{'ubeam_use'} == 0 ){
    $ubeam   = "None";
    $s_ubeam = "0 0";
    $r_ubeam = "0 0";
  }

  print CUR	",".
		"mac_name ".	$mac_name.		",".
		"mac_type ".	$mac_type.		",".  # LWT710対応
		"ip_addr ".	$ip_addr.		",".
		"shift ".	$shiftname.		",".
		"get_time ".	$get_time.		",".
		"sys_time ".	$sys_time.		",".
		"style ".	$current{'style'}.	",".
		"beam ".	$current{'beam'}.	",".
		"s_beam ".	$current{'s_beam'}.	",".
		"r_beam ".	$current{'r_beam'}.	",".
		"ubeam ".	$ubeam.			",".
		"s_ubeam ".	$s_ubeam.		",".
		"r_ubeam ".	$r_ubeam.		",".
		"cloth_len ".	$current{'cloth_len'}.	",".
		"cut_len ".	$current{'cut_len'}.	",".
		"doff_fcst ".	$current{'doff_fcst'}.	",".
		"wout_fcst ".	$current{'wout_fcst'}.	",".
		"uwout_fcst ".	$current{'uwout_fcst'}.	"\n";

  print SET	",".
		"mac_name ".	$mac_name.		",".
		"mac_type ".	$mac_type.		",".  # LWT710対応
		"ip_addr ".	$ip_addr.		",".
		"get_time ".	$get_time.		",".
		"sys_time ".	$sys_time.		",".
		"rtc_time ".	$current{'rtc_time'}.	",".
		"SHIFT_MODE ".	$schedule{'SHIFT_MODE'}.",".
		"SIMPLE ".	$schedule{'SIMPLE'}.	",";
  for( my $i=0; $i<=6; $i++ ){
    print SET	"DAY_$i ".	$schedule{"DAY_".$i}.	",";
  }
  if( defined($schedule{"NAME_0"}) ){ ## 2005.11.07 TMSスキャナー対応
    for( my $i=0; $i<=5; $i++ ){
      print SET	"NAME_$i ".	$schedule{"NAME_".$i}.	",";
    }
    print SET	"DAY_START_TIME ".$schedule{'DAY_START_TIME'}."\n";
  }
  else{
   print SET "\n";
  }
  ++$current_count;
}

################################################################################

sub open_shift_new_file
{
  $shift_count = 0;
  open(SFT,"> $shift_new_dir\\shift.txt");
}

# -------------------------------------------------------------------------------

sub close_shift_new_file
{
  close(SFT);
  if( $shift_count == 0 ){
    unlink("$shift_new_dir\\shift.txt");
  }
}

# -------------------------------------------------------------------------------

sub write_shift
{
  my $ip_addr  = $current{ip_addr};
  my $mac_name = $current{mac_name};

  # 過去データ
  for( my $y=0; $y < 7; $y++ ){		# 7day

    for( my $s=0; $s < 5; $s++ ){	# 5shift
      my $mj = "MJ_s".$s."_y".$y;

      &write_shift2( $mj, $ip_addr, $mac_name, $s, "fixed" );
    }
  }

  # 今日のデータ
  my $cs = $current{shift};
  for( my $s=0; $s<=$cs; $s++ ){  # 現在シフトまで
      my $mj = "MJ_t_s".$s;

      if( $s != $cs ){ &write_shift2( $mj, $ip_addr, $mac_name, $s, "fixed" ); }
      else{            &write_shift2( $mj, $ip_addr, $mac_name, $s, "unfix" ); }
  }
}

# -------------------------------------------------------------------------------

sub write_shift2
{
  my ( $mj, $ip_addr, $mac_name, $shift_num, $fix ) = @_;

  my $tm = $shift{$mj."_tm"};
  if( $tm =~ m/^0/ ){ return; }	# データ無ければファイルに落とさない

  my @d = split(/ /,$tm);
  my $shiftname = sprintf("%04d.%02d.%02d.%d",$d[0],$d[1],$d[2],$shift_num);

  if( &check_shift_fix($shiftname,$mac_name) ){ return; }	# 既に fixed なら上書きしない

  my $ubeam = $shift{$mj."_bn_t"};
  if( $shift{$mj."_bt_use"} == 0 ){ $ubeam = "None"; }

  my $off_prod = "0 0 0 0";
  if( exists($shift{$mj.'_off_prod'}) ){ $off_prod = $shift{$mj.'_off_prod'}; }

  print SFT	"$shiftname.txt,$fix,".		# 本当のファイル名 + "fixed" or "unfix"
		"mac_name ".	$mac_name.		",".
		"mac_type ".	$mac_type.		",".  # LWT710対応
		"ip_addr ".	$ip_addr.		",".
		"shift ".	$shiftname.		",".
		"start ".	$tm.			",".
		"style ".	$shift{$mj.'_sn'}.	",".
		"beam ".	$shift{$mj.'_bn_b'}.	",".
		"ubeam ".	$ubeam.			",".

		"seisan ".	$shift{$mj.'_seisan'}.	",".
		"off_prod ".	$off_prod.		",".  # スキャナオフ時の生産量 2006.1.12 追加
		"run_tm ".	$shift{$mj.'_rt'}.	",".
		"stop_ttm ".	$shift{$mj.'_to'}.	",".
		"s_ct ".	$shift{$mj.'_sc'}.	",".
		"s_tm ".	$shift{$mj.'_st'}.	",";

  if( $mac_type eq "JAT" ){
    print SFT	"tapo1 ".	$shift{$mj.'_tapo1'}.	",".
		"tapo2 ".	$shift{$mj.'_tapo2'}.	",".
		"tapo3 ".	$shift{$mj.'_tapo3'}.	",".
		"tapo4 ".	$shift{$mj.'_tapo4'}.	",".
		"tapo5 ".	$shift{$mj.'_tapo5'}.	",".
		"tapo6 ".	$shift{$mj.'_tapo6'}.	",";
  }

  print SFT	"tail1 ".	$shift{$mj.'_tail1'}.	",".
		"tail2 ".	$shift{$mj.'_tail2'}.	",".
		"tail3 ".	$shift{$mj.'_tail3'}.	",".
		"tail4 ".	$shift{$mj.'_tail4'}.	",".
		"tail5 ".	$shift{$mj.'_tail5'}.	",".
		"tail6 ".	$shift{$mj.'_tail6'}.	"\n";

  ++$shift_count;
  &TMScommon::entry_to_list(\@shift_update_list, "$shiftname.txt");
}

################################################################################

sub open_operator_new_file
{
  $operator_count = 0;
  open(OPE,"> $operator_new_dir\\operator.txt");
}

# -------------------------------------------------------------------------------

sub close_operator_new_file
{
  close(OPE);
  if( $operator_count == 0 ){
    unlink("$operator_new_dir\\operator.txt");
  }
}

# -------------------------------------------------------------------------------

sub write_operator
{
  my $ip_addr  = $current{ip_addr};
  my $mac_name = $current{mac_name};

  for( my $y=0; $y < 7; $y++ ){		# 7day
    my $pm = "PM_y".$y."_p";

    &write_operator2( $pm, $ip_addr, $mac_name, 'fixed' );
  }

  &write_operator2( 'PM_t_p', $ip_addr, $mac_name, 'unfix' );
}

# -------------------------------------------------------------------------------

sub write_operator2
{
  my ( $pm, $ip_addr, $mac_name, $fix ) = @_;

  if( ! defined($operator{$pm.'d_tm'}) ){ return; } ## 2005.11.07 TMSスキャナー対応

  my $tm = $operator{$pm.'d_tm'};
  if( $tm =~ m/^0/ ){ return; }		# データ無ければファイルに落とさない

  my @d = split(/ /,$tm);
  my $day = sprintf("%04d.%02d.%02d",$d[0],$d[1],$d[2]);

  for( my $p=0; $p <6; $p++ ){
    if( $operator{$pm.$p."_ss0"} =~ m/^0/ ){ next; }

    if( &check_operator_fix($day,$mac_name,$p) ){ return; }	# 既に fixed なら上書きしない

    my $ubeam = $operator{$pm.$p.'_bn_t'};
    if( $operator{$pm.$p.'_bt_use'} == 0 ){ $ubeam = 'None'; }

    print OPE	"$day.txt,$fix,".	# 本当のファイル名 + "fixed" or "unfix"
		"mac_name ".	$mac_name.			",".
		"mac_type ".	$mac_type.			",".  # LWT710対応
		"ip_addr ".	$ip_addr.			",".
		"day ".		$day.				",".
		"start ".	$tm.				",".
		"ope_num ".	$p.				",".
		"ope_name ".	$ope_name_list[$p].		",".
		"style ".	$operator{$pm.$p.'_sn'}.	",".
		"beam ".	$operator{$pm.$p.'_bn_b'}.	",".
		"ubeam ".	$ubeam.				",".

		"seisan ".	$operator{$pm.$p.'_seisan'}.	",".
		"run_tm ".	$operator{$pm.$p.'_rt'}.	",".
		"stop_ttm ".	$operator{$pm.$p.'_to'}.	",".
		"s_ct ".	$operator{$pm.$p.'_sc'}.	",".
		"s_tm ".	$operator{$pm.$p.'_st'}.	"\n";

    ++$operator_count;
    &TMScommon::entry_to_list(\@operator_update_list, "$day.txt");
  }
}

################################################################################

sub tm_to_day
{
  my ($tm) = @_;

  if( $tm =~ m/^0/ ){ return ""; }  # データ無しの場合

  # "2005 11 12 1 11 12 13" -> "2005.11.12" に変換

  my @d = split(/ /,$tm);
  my $day = sprintf("%04d.%02d.%02d",$d[0],$d[1],$d[2]);

  return $day;
}

sub set_history
{
  my ($r_key,$r_val) = @_;

  my $key = $$r_key;
  if(    $key =~ m/^MH_t_h([0-9]+)_history/  ){ $history_t[$1]  = $$r_val; }
  elsif( $key =~ m/^MH_d0_h([0-9]+)_history/ ){ $history_d0[$1] = $$r_val; }
  elsif( $key =~ m/^MH_d1_h([0-9]+)_history/ ){ $history_d1[$1] = $$r_val; }

  elsif( $key =~ m/^MH_t_tm/  ){ $history_t_day  = &tm_to_day($$r_val); }
  elsif( $key =~ m/^MH_d0_tm/ ){ $history_d0_day = &tm_to_day($$r_val); }
  elsif( $key =~ m/^MH_d1_tm/ ){ $history_d1_day = &tm_to_day($$r_val); }
}

# -------------------------------------------------------------------------------

sub write_history
{
  my $ip_addr  = $current{ip_addr};
  my $mac_name = $current{mac_name};

  if( $history_t_day  ne "" ){ &write_history2( "unfix", $history_t_day,  $ip_addr, $mac_name, \@history_t  ); }
  if( $history_d0_day ne "" ){ &write_history2( "fixed", $history_d0_day, $ip_addr, $mac_name, \@history_d0 ); }
  if( $history_d1_day ne "" ){ &write_history2( "fixed", $history_d1_day, $ip_addr, $mac_name, \@history_d1 ); }
}

# 新しい停止履歴データをファイルに書き込んでいく
# （更新の場合、古いファイルは消さない。(make_finaleで削除する）

sub write_history2
{
  my ( $fix, $day, $ip_addr, $mac_name, $ref_data ) = @_;

  if( &check_history_fix($day,$mac_name) ){ return; }	# 既に fixed なら上書きしない
							# （この関数で日付のフォルダは作成済み）
  my $fnum = 0;
  my $dir = new DirHandle "$history_dir\\$day";		# ディレクトリのファイルリストを取得する
  while( my $f = $dir->read ){
    if( $f =~ m/^([0-9]+).txt$/ ){
      if( $1 > $fnum ){ $fnum = $1; }		# ファイル名の番号の最大値を求める
    }
  }
  $dir->close;

  ++$fnum;
  my $filename = sprintf("%08d.txt",$fnum);
  if( open(HST, "> $history_dir\\$day\\$filename") ){

    # １行目
    print HST "$fix,".
              "day $day,".
              "ip_addr $ip_addr,".
              "mac_name $mac_name,".
              "mac_type $hist_mac_type\n";  # LWT710対応

    foreach(@$ref_data){
      my @d = split(/ /);	# スペースを , に変換する為
      if( $#d >= 2 ){
        print HST "$d[0],$d[1],$d[2]\n";  # 停止時刻(01:02:03),運転時刻(01:02:03),停止原因番号(1234)
      }
    }

    close(HST);
    &TMScommon::entry_to_list(\@history_update_list, $day);
  }
}

# -------------------------------------------------------------------------------


################################################################################
1;
