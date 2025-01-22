use Time::HiRes qw(gettimeofday);

sub measure {
    my ($data, $pattern) = @_;

    my $start = Time::HiRes::gettimeofday();

    my $count = () = $data =~ /$pattern/g;

    my $elapsed = (Time::HiRes::gettimeofday() - $start) * 1e3;

    printf("%f - %d\n", $elapsed, $count);
}

# sub measure {
#   my ($data, $pattern) = @_;

#   my $start = Time::HiRes::gettimeofday();

#   # 修改这行，使用 =~ m/^pattern$/ 进行完全匹配
#   my $match = $data =~ /^($pattern)$/;

#   my $elapsed = (Time::HiRes::gettimeofday() - $start) * 1e3;

#   # 修改输出，显示是否匹配（1表示匹配，空或0表示不匹配）
#   printf("%f - %d\n", $elapsed, $match ? 1 : 0);
# }

if (@ARGV != 2) {
  die "Usage: ./benchmark.pl <filename>\n";
}

my ($filename) = @ARGV[1];

open my $fh, '<', $filename or die 'Could not open file.';
my $text;
read $fh, $data, -s $filename;
close $fh;
measure $data, @ARGV[0];