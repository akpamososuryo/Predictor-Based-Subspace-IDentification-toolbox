function generateDvar2frdFixture(outputPath)
%generateDvar2frdFixture  Write MATLAB reference fixture for dvar2frd parity tests.
%
% Usage:
%   testutils.generateDvar2frdFixture
%   testutils.generateDvar2frdFixture('fixtures/matlab_reference/dvar2frd_fixture.mat')

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dvar2frd_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

p = 4;
l = 2;
r = 1;
h = 0.05;
w = linspace(0.2, 2.0, 6);

rng(91);
m = l + r;
VARX = 0.2 .* randn(l, p * m + r);

nParam = p * l * (l + r) + r * l;
P = 1e-3 .* eye(nParam);

[G, covG] = dvar2frd(P, w, h, p, VARX);

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dvar2frd(VARX mode) parity checks';
meta.createdBy = 'testutils.generateDvar2frdFixture';

save(outputPath, 'meta', 'P', 'w', 'h', 'p', 'VARX', 'G', 'covG');

fprintf('Wrote fixture: %s\n', outputPath);
end
