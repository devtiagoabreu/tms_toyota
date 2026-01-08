package TMSDATAindex;

###################################################################################################
#
# TMSDATAindex.pm
#
###################################################################################################

use strict;
use DirHandle;
use Time::Local;

use TMSstr;
use TMScommon;
use TMSstophist;

###################################################################################################

my $tmsdata_dir = "..\\..\\tmsdata";

my $index_dir          = "$tmsdata_dir\\index";

my $shift_shift_dir    = "$tmsdata_dir\\shift-shift";
my $shift_date_dir     = "$tmsdata_dir\\shift-date";
my $shift_week_dir     = "$tmsdata_dir\\shift-week";
my $shift_month_dir    = "$tmsdata_dir\\shift-month";

my $operator_date_dir  = "$tmsdata_dir\\operator-date";
my $operator_week_dir  = "$tmsdata_dir\\operator-week";
my $operator_month_dir = "$tmsdata_dir\\operator-month";

my $current_dir        = "$tmsdata_dir\\current";

###################################################################################################

sub make_index
{
  my ($phase) = @_;

  # index 以外は、make_index.pm の単体呼び出し用

  &TMScommon::make_dir( $tmsdata_dir );

  &TMScommon::make_dir( $shift_shift_dir );
  &TMScommon::make_dir( $shift_date_dir );
  &TMScommon::make_dir( $shift_week_dir );
  &TMScommon::make_dir( $shift_month_dir );
  &TMScommon::make_dir( $operator_date_dir );
  &TMScommon::make_dir( $operator_week_dir );
  &TMScommon::make_dir( $operator_month_dir );
  &TMScommon::make_dir( $current_dir );

  &TMScommon::make_dir( $index_dir );
  # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
  system( "del /Q /F $index_dir\\*.*" );

  &TMScommon::disp_percent(100,0, $phase); # 0%

  &make_shift_index("shift");
  &make_shift_index("date");

  &TMScommon::disp_percent(100,20); # 20%

  &make_shift_index("week");
  &make_shift_index("month");

  &TMScommon::disp_percent(100,40); # 40%

  &make_operator_index("date");

  &TMScommon::disp_percent(100,60); # 60%

  &make_operator_index("week");
  &make_operator_index("month");

  &TMScommon::disp_percent(100,80); # 80%

  &make_current_index();
  &make_stophist_index();

  &TMScommon::disp_percent(100,101); # 100% done
}

###################################################################################################
# week のデータのみ更新（週設定変更用）

sub make_week_index
{
  my ($phase) = @_;

  # index 以外は、make_index.pm の単体呼び出し用

  &TMScommon::make_dir( $tmsdata_dir );

  &TMScommon::make_dir( $shift_week_dir );
  &TMScommon::make_dir( $operator_week_dir );

  &TMScommon::make_dir( $index_dir );

  &TMScommon::disp_percent(100,0, $phase); # 0%

  &make_shift_index("week");

  &TMScommon::disp_percent(100,40); # 40%

  &make_operator_index("week");

  &TMScommon::disp_percent(100,101); # 100% done
}

###################################################################################################

sub write_list
{
  my( $r_list, $fname, $rev ) = @_;

  @$r_list = sort @$r_list;

  open(LIST, "> $fname" );
  if( $rev ){
    for( my $i = $#$r_list; $i>=0; $i-- ){ print LIST "$$r_list[$i]\n"; }
  }
  else{
    foreach(@$r_list){ print LIST "$_\n"; }
  }
  close(LIST);
}

###################################################################################################

sub make_shift_index
{
  my ($mode) = @_;

  my $dname;
  my $period_fname;
  my $loom_fname;
  my $style_fname;
  my $old;

  if(    $mode eq "shift" ){
    $dname        = $shift_shift_dir;
    $period_fname = "$index_dir\\shift_shift.txt";
    $loom_fname   = "$index_dir\\loom_s.txt";
    $style_fname  = "$index_dir\\style_s.txt";
    $old = 2;
  }
  elsif( $mode eq "date"  ){
    $dname        = $shift_date_dir;
    $period_fname = "$index_dir\\shift_date.txt";
    $loom_fname   = "$index_dir\\loom_d.txt";
    $style_fname  = "$index_dir\\style_d.txt";
    $old = 2;
  }
  elsif( $mode eq "week"  ){
    $dname        = $shift_week_dir;
    $period_fname = "$index_dir\\shift_week.txt";
    $loom_fname   = "$index_dir\\loom_w.txt";
    $style_fname  = "$index_dir\\style_w.txt";
    $old = 5;
  }
  elsif( $mode eq "month" ){
    $dname        = $shift_month_dir;
    $period_fname = "$index_dir\\shift_month.txt";
    $loom_fname   = "$index_dir\\loom_m.txt";
    $style_fname  = "$index_dir\\style_m.txt";
    $old = 11;
  }

  # -------------------------------------------------------------------------------

  my @file = ();
  my $dir = new DirHandle $dname;	# ディレクトリのファイルリストを取得する
  while( my $f = $dir->read ){
    if( $f =~ m/^\d{4}\.\d{2}\.[0-9\.]*txt$/ ){ push(@file,$f); }	# dirの結果を配列に入れる
  }
  $dir->close;
  @file = sort @file;	# 配列をソートする。

  my @period_list = ();
  my @loom_list   = ();
  my @style_list  = ();

  foreach my $fname ( @file ){
    my $period = $fname;
    $period =~ s/.txt$//;

    if( ($mode eq "shift") || ($mode eq "date") ){
      # 曜日を作る
      my @d = split(/\./,$period);
      my $y_date = timelocal(0,0,0,$d[2],($d[1] -1),($d[0] -1900));
      my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($y_date);
      &TMScommon::entry_to_list(\@period_list, "$period $wday" );
    }
    else{
      &TMScommon::entry_to_list(\@period_list, $period );
    }

    open(IN,"< $dname\\$fname");
    while(<IN>){
      if( m/,style ([^,]+)/    ){ &TMScommon::entry_to_list(\@style_list, $1); }
      if( m/,mac_name ([^,]+)/ ){ &TMScommon::entry_to_list(\@loom_list, $1);  }
    }
    close(IN);
  }

  &write_list( \@period_list, $period_fname, 1 );
  &write_list( \@loom_list,   $loom_fname,   0 );
  &write_list( \@style_list,  $style_fname,  0 );

}

###################################################################################################

sub make_operator_index
{
  my ($mode) = @_;

  my $dname;
  my $period_fname;
  my $operator_fname;
  my $old;

  if(    $mode eq "date"  ){
    $dname          = $operator_date_dir;
    $period_fname   = "$index_dir\\opedata_date.txt";
    $operator_fname = "$index_dir\\operator_d.txt";
    $old = 2;
  }
  elsif( $mode eq "week"  ){
    $dname          = $operator_week_dir;
    $period_fname   = "$index_dir\\opedata_week.txt";
    $operator_fname = "$index_dir\\operator_w.txt";
    $old = 5;
  }
  elsif( $mode eq "month" ){
    $dname          = $operator_month_dir;
    $period_fname   = "$index_dir\\opedata_month.txt";
    $operator_fname = "$index_dir\\operator_m.txt";
    $old = 11;
  }

  # -------------------------------------------------------------------------------

  my @file = ();
  my $dir = new DirHandle $dname;	# ディレクトリのファイルリストを取得する
  while( my $f = $dir->read ){
    if( $f =~ m/^\d{4}\.\d{2}\.[0-9\.]*txt$/ ){ push(@file,$f); }	# dirの結果を配列に入れる
  }
  $dir->close;
  @file = sort @file;	# 配列をソートする。

  my @period_list   = ();
  my @operator_list = ();

  foreach my $fname ( @file ){
    my $period = $fname;
    $period =~ s/.txt$//;

    if( $mode eq "date" ){
      # 曜日を作る
      my @d = split(/\./,$period);
      my $y_date = timelocal(0,0,0,$d[2],($d[1] -1),($d[0] -1900));
      my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($y_date);
      &TMScommon::entry_to_list(\@period_list, "$period $wday" );
    }
    else{
      &TMScommon::entry_to_list(\@period_list, $period );
    }

    open(IN,"< $dname\\$fname");
    while(<IN>){
      if( m/,ope_name ([^,]+)/ ){ &TMScommon::entry_to_list(\@operator_list, $1); }
   }
    close(IN);
  }

  &write_list( \@period_list,   $period_fname,   1 );
  &write_list( \@operator_list, $operator_fname, 0 );

}


###################################################################################################

sub make_current_index
{
  my @style_list = ();
  my @loom_list = ();

  my $fname = "$current_dir\\current.txt";
  if( -f $fname ){
    open(IN,"< $fname");
    while(<IN>){
      if( m/,style ([^,]+)/    ){ &TMScommon::entry_to_list(\@style_list, $1); }
      if( m/,mac_name ([^,]+)/ ){ &TMScommon::entry_to_list(\@loom_list, $1);  }
    }
    close(IN);

    &write_list( \@style_list, "$index_dir\\current_style.txt", 0);
    &write_list( \@loom_list,  "$index_dir\\current_loom.txt",  0);
  }
}

###################################################################################################
# 機能    停台履歴報告対象を選択するための候補(期間、機台)を作成する
# 引数   : なし
# 戻り値 : なし

sub make_stophist_index
{
  # 停止履歴フォルダの一覧を取得
  my ($stophist_dir, @stophist_subdir) = &TMSstophist::get_stophist_dir();

  ### 「期間」のindexを作成 ###
  my @period_list = ();
  foreach my $subdir ( @stophist_subdir ){

    # 日付関数がエラーするフォルダ名は無視する
    my @d = split( /\./, $subdir );
    my $y_date;
    eval{ $y_date = timelocal(0,0,0,$d[2],($d[1] -1),($d[0] -1900)); };
    if( $@ ){ next; }

    # 曜日番号取得
    my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($y_date);

    &TMScommon::entry_to_list( \@period_list, "$subdir $wday" );
  }
  &write_list( \@period_list, "$index_dir\\history_date.txt", 1 );  # 逆順ソート


  ### 「機台名」のindexを作成 ###
  my @loom_list   = ();
  foreach my $subdir ( @stophist_subdir ){

    if( open(INDEX, "< $stophist_dir\\$subdir\\index.txt") ){
      while( <INDEX> ){
        chomp $_;
        my @d = split(/,/, $_);
        if( $#d >= 2 ){
          &TMScommon::entry_to_list( \@loom_list, $d[2] );  # 機台名は３項目目
        }
      }
      close(INDEX);
    }
  }
  &write_list( \@loom_list, "$index_dir\\history_loom.txt", 0 );
}

###################################################################################################
1;
