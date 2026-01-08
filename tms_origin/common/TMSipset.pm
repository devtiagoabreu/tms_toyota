package TMSipset;

###################################################################################################
#
# TMSipset.pm
#
###################################################################################################

use strict;

use TMScommon;

###################################################################################################

sub get_ip_set_list
{
  my @list = ();

  if( open(IPADDR,'< ../../tmsdata/setting/ipaddress.txt') ){
    while(<IPADDR>){
      $_ =~ s/\n$//;		# 改行コードを削除。
      push(@list,$_);
    }
    close(IPADDR);

    @list = sort @list;
    for( my $i=0; $i<=$#list; $i++ ){
      $list[$i] =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
      $list[$i] =~ s/^\s//;	# 行頭のスペースを削除する。
    }
  }
  #else{
  #  @list = ('172 17 1 1 1');
  #}

  return @list;
}

###################################################################################################

sub save_ip_set_list
{
  my ($r_list) = @_;

  &TMScommon::make_dir('../../tmsdata');
  &TMScommon::make_dir('../../tmsdata/setting');
  my $setfile = '../../tmsdata/setting/ipaddress.txt';

  if( $#$r_list >= 0 ){
    if( open(IPADDR, "> $setfile") ){
      foreach(@$r_list){ print IPADDR "$_\n"; }
      close(IPADDR);
    }
  }else{
    unlink $setfile;
  }
}

###################################################################################################
# for loom data

sub get_all_ip_list
{
  my @set_list = get_ip_set_list();

  my @list = ();
  foreach( @set_list ){
    my @data = split(/ /);
    for( my $i=$data[3]; $i<=$data[4]; $i++ ){
      push( @list, "$data[0].$data[1].$data[2].$i" );
    }
  }

  return @list;
}

###################################################################################################

sub get_name_ip_list
{
  my ( $r_name_list, $r_ip_list ) = @_;

  my @ip_list = @$r_ip_list;

  my @data_list = ();
  if( open(IN,'< ../../tmsdata/current/current.txt') ){
    while(<IN>){
      my $mac_name = "";
      my $ip_addr  = "";
      my $get_time = "";
      if( m/,mac_name ([^,]+)/ ){
        $mac_name = $1;
        if( m/,ip_addr ([^,]+)/ ){
          $ip_addr = $1;
          if( m/,get_time ([^,]+)/ ){  # データ取得日の桁数を合わせる
            my @gt = split(/ /,$1,7);
	    $get_time = sprintf( "%04d/%02d/%02d %02d:%02d:%02d", $gt[0],$gt[1],$gt[2],$gt[4],$gt[5],$gt[6] );
	    push( @data_list, "$get_time,$mac_name,$ip_addr" );
	  }
        }
      }
    }
    close(IN);
  }
  @data_list = sort @data_list;	# データ取得日でソートする(同じ機台名あったら、後勝ちにする為)

  # IPで機台名が引ける様にする。
  my %name_tbl = ();
  foreach( @data_list ){
    my @val = split(/,/);
    my $mac_name = $val[1];
    my $ip_addr  = $val[2];
    $name_tbl{$ip_addr} = $mac_name;
  }

  # 要求されたIPリストから、機台名・IPのリスト作成
  my @name_ip_list = ();
  foreach my $ip (@ip_list){
    my $name = $ip;
    if( exists( $name_tbl{$ip} ) ){ $name = $name_tbl{$ip}; }
    push( @name_ip_list, "$name,$ip" );
  }
  @name_ip_list = sort @name_ip_list;

  @ip_list = ();
  my @name_list = ();
  foreach( @name_ip_list ){
    my @val = split(/,/);	# 機台名とIPを分離
    push( @name_list, $val[0] );
    push( @ip_list,   $val[1] );
  }

  @$r_name_list = @name_list;
  @$r_ip_list   = @ip_list;
}

###################################################################################################
1;
