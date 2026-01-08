package TMSedit;

###################################################################################################
#
# TMSedit.pm
#
###################################################################################################

use strict;
use DirHandle;

use TMScommon;

###################################################################################################

sub get_month_file_list
{
  my ($month,$data_dir,$r_month_list,$r_period_list) = @_;

  # 月、ファイルリスト作成
  my @file_list = ();

  if( -d $data_dir ){
    my $dir = new DirHandle $data_dir;		# ディレクトリのファイルリストを取得する
    while( my $f = $dir->read ){
      if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.[0-9\.]*txt$/ ){
        $f =~ s/\.txt$//;			# 拡張子削除
        push(@file_list, $f);
        my @d = split(/\./,$f);
        &TMScommon::entry_to_list( $r_month_list, "$d[0].$d[1]" );
      }
    }
    $dir->close;

    @$r_month_list = sort @$r_month_list;	# 配列をソートする。
    @file_list     = sort @file_list;		# 配列をソートする。
  }
  if( $#$r_month_list < 0 ){ return $month; }

  # 月が指定されていない場合、最新月
  if( length($month) == 0 ){ $month = $$r_month_list[$#$r_month_list]; }
  else{
    for( my $i=0; $i<=$#$r_month_list; $i++ ){
      if( $$r_month_list[$i] eq $month ){ last; }
      # 選択された月がない場合、最新月
      if( $i == $#$r_month_list ){ $month = $$r_month_list[$#$r_month_list]; }
    }
  }
  
  # 選択された月のみ、期間にする。
  my $mstr = $month;
  $mstr =~ s/\./\\./g;	# . をエスケープする。
  foreach( @file_list ){
    if( m/^$mstr/ ){ push(@$r_period_list, $_); }
  }
  @$r_period_list = sort @$r_period_list;

  return $month;
}

###################################################################################################

sub make_edit_index
{
  my ($sel_data,$month,$data_dir,$r_period_list,$r_loom_list,$r_style_list) = @_;

  my $file_header;
  if( $sel_data eq 'shift'    ){ $file_header = "s_"; }
  if( $sel_data eq 'operator' ){ $file_header = "o_"; }

  &TMScommon::make_dir( "..\\..\\tmsdata\\index" );
  &TMScommon::make_dir( "..\\..\\tmsdata\\index\\edit" );
  my $loom_index  = "..\\..\\tmsdata\\index\\edit\\$file_header"."loom$month.txt";
  my $style_index = "..\\..\\tmsdata\\index\\edit\\$file_header"."style$month.txt";

  if( (-f $loom_index) && ( -f $style_index) ){	# 既にファイルがある場合
    if( open(IN,"< $loom_index") ){
      while(<IN>){
        my $data = $_;
        $data =~ s/\n$//;
        push(@$r_loom_list,$data);
      }
      close(IN);
    }
    if( open(IN,"< $style_index") ){
      while(<IN>){
        my $data = $_;
        $data =~ s/\n$//;
        push(@$r_style_list,$data);
      }
      close(IN);
    }
  }
  else{		# リストがない場合は作る。
    foreach my $fname ( @$r_period_list ){
      if( open(IN,"< $data_dir\\$fname.txt") ){
        while(<IN>){
          if( m/,mac_name ([^,]*)/ ){ &TMScommon::entry_to_list($r_loom_list,  $1); }
          if( m/,style ([^,]*)/    ){ &TMScommon::entry_to_list($r_style_list, $1); }
        }
        close(IN);
      }
    }
    @$r_loom_list = sort @$r_loom_list;
    if( open(OUT,"> $loom_index") ){		# 再利用できる様に保存する
      foreach(@$r_loom_list){ print OUT "$_\n"; }
      close(OUT);
    }
    @$r_style_list = sort @$r_style_list;
    if( open(OUT,"> $style_index") ){		# 再利用できる様に保存する
      foreach(@$r_style_list){ print OUT "$_\n"; }
      close(OUT);
    }
  }
}

###################################################################################################
1;
