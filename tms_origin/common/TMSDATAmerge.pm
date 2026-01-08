package TMSDATAmerge;

###################################################################################################
#
# TMSDATAmerge.pm
#
###################################################################################################

use strict;
use DirHandle;

use TMSstr;
use TMScommon;

###################################################################################################

my $debug_mode = 0;	# 中間ファイルを、消す。
#my $debug_mode = 1;	# 中間ファイルを、残す。

my $tmsdata_dir   = "..\\..\\tmsdata";
my $loom_dir      = "$tmsdata_dir\\loom";

my $current_dir  = "$tmsdata_dir\\current";
my $shift_dir    = "$tmsdata_dir\\shift";
my $operator_dir = "$tmsdata_dir\\operator";

my $current_new_dir  = "$current_dir\\newdata";
my $shift_new_dir    = "$shift_dir\\newdata";
my $operator_new_dir = "$operator_dir\\newdata";

################################################################################

sub merge_data
{
  my ($phase) = @_;

  if( $debug_mode ){
    print "\n-- TMSDATAmerge::debug_mode = 1 --\n";
  }

  &TMScommon::make_dir( $current_dir );

  &TMScommon::disp_percent(100,0, $phase); # 0%

  &merge_current_data( "current.txt" );

  &TMScommon::disp_percent(100,20); # 20%

  &merge_current_data( "setting.txt" );

  &TMScommon::disp_percent(100,40); # 40%

  &merge_shift_data();

  &TMScommon::disp_percent(100,80); # 80%

  &merge_operator_data();

  &TMScommon::disp_percent(100,101); # 100% done

  # ------------------------------------------------------------
  # データ編集画面用index削除

  my $edit_index_dir = "$tmsdata_dir\\index\\edit";
  if( -d $edit_index_dir ){
    # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
    system( "del /Q /F $edit_index_dir\\*.*" );
  }
}

################################################################################

sub merge_current_data
{
  my ($fname) = @_;

  my @new_data = ();	# 新規データ	(sort不可)
  my @old_data = ();	# 既存のデータ	(sort不可)

  my %new_index = ();	# key:mac_name, val:@new_dataの配列番号
  my %old_index = ();	# 

  my @mac_list = ();	# 機台名のリスト(データを機台名でソートする為)
  my @ym_list  = ();	# 年月のリスト(古い年月を計算する為)

  if( open(NEW,"< $current_new_dir\\$fname") ){	# 新規ファイルの読み込み
    @new_data = <NEW>;
    close(NEW);

    if( $debug_mode == 0 ){ unlink( "$current_new_dir\\$fname" ); }

    for( my $i=0; $i<=$#new_data; $i++ ){
      my $data = $new_data[$i];

      if( $data =~ m/,sys_time ([^,]+)/ ){
        my $ym = &TMScommon::get_ym_by_space( $1 );

        if( $data =~ m/,mac_name ([^,]+)/ ){
          my $mac_name = $1;

          unless( exists( $new_index{$mac_name} ) ){  # 同じ機台名の場合、早い者勝ち
            $new_index{$mac_name} = $i;
            push(@mac_list,$mac_name);
            push(@ym_list,$ym);
          }
        }
      }
    }
    if( $#ym_list < 0 ){ return; }	# 新しいデータ無し

    if( open(OLD,"< $current_dir\\$fname") ){	# 既存ファイルの読み込み
      @old_data = <OLD>;
      close(OLD);

      for( my $i=0; $i<=$#old_data; $i++ ){
        my $data = $old_data[$i];

        if( $data =~ m/,sys_time ([^,]+)/ ){
          my $ym = &TMScommon::get_ym_by_space( $1 );

          if( $data =~ m/,mac_name ([^,]+)/ ){
            my $mac_name = $1;

            unless( exists( $new_index{$mac_name} ) ){
              unless( exists( $old_index{$mac_name} ) ){  # 同じ機台名の場合、早い者勝ち
                $old_index{$mac_name} = $i;
                push(@mac_list,$mac_name);
                push(@ym_list,$ym);
              }
            }
          }
        }
      }
    }

    my @ym_list = sort @ym_list;
    my $old_ym = &TMScommon::get_old_ym( $ym_list[$#ym_list], 1 );  # 最新データの１ヶ月前の年月

    if( open(DES,"> $current_dir\\$fname") ){	# マージ後のデータを書き出し

      @mac_list = sort @mac_list;		# 機台名でソート
      foreach( @mac_list ){

        my $data = "";
        if(    exists( $new_index{$_} ) ){ $data = $new_data[$new_index{$_}]; }
        elsif( exists( $old_index{$_} ) ){ $data = $old_data[$old_index{$_}]; }
        else{ next; }

        if( $data =~ m/,sys_time ([^,]+)/ ){
          my $ym = &TMScommon::get_ym_by_space( $1 );
          if( $ym < $old_ym ){ next; }		# 古いデータは捨てる。
        }

        print DES $data;
      }

      close(DES);
    }
  }
}

################################################################################

sub merge_shift_data
{
  &TMScommon::make_dir( $shift_dir );

  my @file_list = ();	# 既存データのファイル名
  my @ym_list = ();	# 既存データ＋新規データの年月

  if( open(UPD,"< $shift_new_dir\\shift_update.txt") ){	# 更新されたファイルを取得
    while(<UPD>){
      my $ym = &TMScommon::get_ym_by_dot( $_ );
      &TMScommon::entry_to_list( \@ym_list, $ym );
    }
    close(UPD);
  }
  if( $#ym_list < 0 ){ return; }	# 新しいデータ無し

  my $dir = new DirHandle $shift_dir;	# ディレクトリのファイルリストを取得する
  while( my $f = $dir->read ){
    if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.\d\.txt$/ ){
      push(@file_list,$f);
      my $ym = &TMScommon::get_ym_by_dot( $f );
      &TMScommon::entry_to_list( \@ym_list, $ym );
    }
  }
  $dir->close;

  @ym_list = sort @ym_list;
  my $old_ym = &TMScommon::get_old_ym( $ym_list[$#ym_list], 11 );  # 最新データの11ヶ月前の年月

  # データマージ処理 ここから -------------------------

  if( -f "$shift_new_dir\\shift.txt" ){
    # 新規データをソート
    # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
    system( "sort $shift_new_dir\\shift.txt /O $shift_new_dir\\shift_sort.txt" );

    if( open(NEW,"< $shift_new_dir\\shift_sort.txt") ){	# ソート済み新規データ読み込み

      my $fname;
      my @new_data = ();
      my $ym;

      while(<NEW>){		# １行目のデータ
        my @s = split(/,/,$_,2);
        $fname = $s[0];			# $s[0]:ファイル名
        push(@new_data,$s[1]);		# $s[1]:データ
        last;
      }
      while(<NEW>){		# ２行目以降のデータ
        my @s = split(/,/,$_,2);
        if( $fname ne $s[0] ){  			# ファイル名が前回と不一致なら
          $ym = &TMScommon::get_ym_by_dot( $fname );
          if( $ym >= $old_ym ){				# 年月が古くなければ
            &merge_shift_data2($fname, \@new_data );	# マージ処理。
          }
          $fname = $s[0];
          @new_data = ();
        }
        push(@new_data,$s[1]);
      }
							# 最後に残ったデータ
      $ym = &TMScommon::get_ym_by_dot( $fname );
      if( $ym >= $old_ym ){				# 年月が古くなければ
        &merge_shift_data2($fname, \@new_data);		# マージ処理。
      }
      close(NEW);
  
    }

    if( $debug_mode == 0 ){ 
      unlink( "$shift_new_dir\\shift.txt" );
      unlink( "$shift_new_dir\\shift_sort.txt" );
    }
  }

  # 古い既存データの削除 --------------------------------------

  @file_list = sort @file_list;
  foreach my $fname (@file_list){
    my $ym = &TMScommon::get_ym_by_dot( $fname );
    if( $ym < $old_ym ){ unlink( "$shift_dir\\$fname" ); }
    else{ last; }
  }

}

# -------------------------------------------------------------------------------
# 単一ファイルのマージ処理
# -------------------------------------------------------------------------------

sub merge_shift_data2
{
  my ($fname, $r_new_data) = @_;

  # @$r_new_data	# 新規データ	(sort不可)
  my @old_data = ();	# 既存のデータ	(sort不可)

  my %new_index = ();	# key:mac_name, val:@new_dataの配列番号
  my %old_index = ();	#

  my @mac_list = ();	# 機台名のリスト(データを機台名でソートする為)

  for( my $i=0; $i<=$#$r_new_data; $i++ ){
    my $data = $$r_new_data[$i];

    if( $data =~ m/,mac_name ([^,]+)/ ){
      my $mac_name = $1;

      unless( exists( $new_index{$mac_name} ) ){	# 同じ機台名の場合、早い者勝ち
        $new_index{$mac_name} = $i;			# $i = 行番号
        push(@mac_list,$mac_name);
      }
    }
  }

  if( open(OLD,"< $shift_dir\\$fname") ){	# 既存ファイルの読み込み
    @old_data = <OLD>;
    close(OLD);

    for( my $i=0; $i<=$#old_data; $i++ ){
      my $data = $old_data[$i];

      if( $data =~ m/,mac_name ([^,]+)/ ){
        my $mac_name = $1;
        unless( exists( $new_index{$mac_name} ) ){
          unless( exists( $old_index{$mac_name} ) ){	# 同じ機台名の場合、早い者勝ち
            $old_index{$mac_name} = $i;			# $i = 行番号
            push(@mac_list,$mac_name);
          }
        }
      }
    }
  }

  if( open(DES,"> $shift_dir\\$fname") ){	# マージ後のデータを書き出し

    @mac_list = sort @mac_list;			# 機台名でソート
    foreach( @mac_list ){
      if(    exists( $new_index{$_} ) ){  print DES $$r_new_data[$new_index{$_}]; }
      elsif( exists( $old_index{$_} ) ){  print DES $old_data[$old_index{$_}]; }
    }

    close(DES);
  }
}

################################################################################

sub merge_operator_data
{
  &TMScommon::make_dir( $operator_dir );

  my @file_list = ();	# 既存データのファイル名
  my @ym_list = ();	# 既存データ＋新規データの年月

  if( open(UPD,"< $operator_new_dir\\operator_update.txt") ){	# 更新されたファイルを取得
    while(<UPD>){
      my $ym = &TMScommon::get_ym_by_dot( $_ );
      &TMScommon::entry_to_list( \@ym_list, $ym );
    }
    close(UPD);
  }
  if( $#ym_list < 0 ){ return; }	# 新しいデータ無し

  my $dir = new DirHandle $operator_dir;	# ディレクトリのファイルリストを取得する
  while( my $f = $dir->read ){
    if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.txt$/ ){
      push(@file_list,$f);
      my $ym = &TMScommon::get_ym_by_dot( $f );
      &TMScommon::entry_to_list( \@ym_list, $ym );
    }
  }
  $dir->close;

  @ym_list = sort @ym_list;
  my $old_ym = &TMScommon::get_old_ym( $ym_list[$#ym_list], 11 );  # 最新データの11ヶ月前の年月


  # データマージ処理 ここから -------------------------

  if( -f "$operator_new_dir\\operator.txt" ){
    # 新規データをソート
    # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
    system( "sort $operator_new_dir\\operator.txt /O $operator_new_dir\\operator_sort.txt" );

    if( open(NEW,"< $operator_new_dir\\operator_sort.txt") ){	# ソート済み新規データ読み込み

      my $fname;
      my @new_data = ();
      my $ym;

      while(<NEW>){		# １行目のデータ
        my @s = split(/,/,$_,2);
        $fname = $s[0];			# $s[0]:ファイル名
        push(@new_data,$s[1]);		# $s[1]:データ
        last; 
     }
      while(<NEW>){		# ２行目以降のデータ
        my @s = split(/,/,$_,2);
        if( $fname ne $s[0] ){  			# ファイル名が前回と不一致なら
          $ym = &TMScommon::get_ym_by_dot( $fname );
          if( $ym >= $old_ym ){				# 年月が古くなければ
            &merge_operator_data2($fname, \@new_data);	# マージ処理。
          }
          $fname = $s[0];
          @new_data = ();
        }
        push(@new_data,$s[1]);
      }
							# 最後に残ったデータ
      $ym = &TMScommon::get_ym_by_dot( $fname );
      if( $ym >= $old_ym ){				# 年月が古くなければ
        &merge_operator_data2($fname, \@new_data);	# マージ処理。
      }
      close(NEW);

    }

    if( $debug_mode == 0 ){ 
      unlink( "$operator_new_dir\\operator.txt" );
      unlink( "$operator_new_dir\\operator_sort.txt" );
    }
  }

  # 古い既存データの削除 --------------------------------------

  @file_list = sort @file_list;
  foreach my $fname (@file_list){
    my $ym = &TMScommon::get_ym_by_dot( $fname );
    if( $ym < $old_ym ){ unlink( "$operator_dir\\$fname" ); }
    else{ last; }
  }

}

# -------------------------------------------------------------------------------
# 単一ファイルのマージ処理
# -------------------------------------------------------------------------------

sub merge_operator_data2
{
  my ($fname, $r_new_data) = @_;

  # @$r_new_data	# 新規データ	(sort不可)
  my @old_data = ();	# 既存のデータ	(sort不可)

  my %new_index = ();	# key:mac_name, val:@new_dataの配列番号
  my %old_index = ();	# 

  my @mac_list = ();	# 機台名のリスト(データを機台名でソートする為)

  for( my $i=0; $i<=$#$r_new_data; $i++ ){
    my $data = $$r_new_data[$i];

    if( $data =~ m/,mac_name ([^,]+)/ ){
      my $mac_name = $1;

      unless( exists( $new_index{$mac_name} ) ){	# 同じ機台名の場合、早い者勝ち
        if( $data =~ m/,ope_num ([^,]+)/ ){
          my $ope_num = $1;
          my $key = "$mac_name $ope_num";
          $new_index{$key} = $i;
          push(@mac_list,$key);
        }
      }
    }
  }

  if( open(OLD,"< $operator_dir\\$fname") ){	# 既存ファイルの読み込み
    @old_data = <OLD>;
    close(OLD);

    for( my $i=0; $i<=$#old_data; $i++ ){
      my $data = $old_data[$i];

      if( $data =~ m/,mac_name ([^,]+)/ ){
        my $mac_name = $1;

        if( $data =~ m/,ope_num ([^,]+)/ ){
          my $ope_num = $1;
          my $key = "$mac_name $ope_num";

          unless( exists( $new_index{$key} ) ){
            unless( exists( $old_index{$key} ) ){	# 同じ機台名の場合、早い者勝ち
              $old_index{$key} = $i;
              push(@mac_list,$key);
            }
          }
        }
      }
    }
  }

  if( open(DES,"> $operator_dir\\$fname") ){	# マージ後のデータを書き出し

    @mac_list = sort @mac_list;		# 機台名でソート
    foreach( @mac_list ){
      if(    exists( $new_index{$_} ) ){  print DES $$r_new_data[$new_index{$_}]; }
      elsif( exists( $old_index{$_} ) ){  print DES $old_data[$old_index{$_}]; }
    }
    close(DES);
  }
}

################################################################################
1;
