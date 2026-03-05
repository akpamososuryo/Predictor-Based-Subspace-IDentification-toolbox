function generateDordvarmaxFixture(outputPath)
%generateDordvarmaxFixture  Write MATLAB reference fixture for dordvarmax parity tests.
%
% Usage:
%   testutils.generateDordvarmaxFixture
%   testutils.generateDordvarmaxFixture('fixtures/matlab_reference/dordvarmax_fixture.mat')

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dordvarmax_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

d = testutils.makeDordvarxData('seed', 73);

[S_base, X_base, VARMAX_base, U_base] = dordvarmax( ...
    d.u, d.y, d.f, d.p, 'gradient', 1e-6, 'none', 'gcv', 0, 0);

[S_weight1, X_weight1, VARMAX_weight1, U_weight1] = dordvarmax( ...
    d.u, d.y, d.f, d.p, 'els', 1e-6, 'none', 'gcv', 1, 0);

[S_noD, X_noD, VARMAX_noD, U_noD] = dordvarmax( ...
    d.u, d.y, d.f, d.p, 'gradient', 1e-6, 'none', 'gcv', 0, 1);

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dordvarmax baseline/weight/noD parity checks';
meta.createdBy = 'testutils.generateDordvarmaxFixture';

u_base = d.u; %#ok<NASGU>
y_base = d.y; %#ok<NASGU>
f_base = d.f; %#ok<NASGU>
p_base = d.p; %#ok<NASGU>

save(outputPath, ...
    'meta', ...
    'u_base', 'y_base', 'f_base', 'p_base', ...
    'S_base', 'X_base', 'VARMAX_base', 'U_base', ...
    'S_weight1', 'X_weight1', 'VARMAX_weight1', 'U_weight1', ...
    'S_noD', 'X_noD', 'VARMAX_noD', 'U_noD');

fprintf('Wrote fixture: %s\n', outputPath);
end
