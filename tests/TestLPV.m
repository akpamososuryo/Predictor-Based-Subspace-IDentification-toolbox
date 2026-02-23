classdef TestLPV < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function lordvarxPipelineRunsAndOutputsSane(testCase)
            [u, y, mu, meta] = testutils.makeLpvData('N', 600, 'seed', 31, 'noiseStd', 0.04, 'rhoType', 'random');

            f = 6;
            p = 12;
            n = 1;

            [S, X] = lordvarx(u, y, mu, f, p);

            testCase.verifyNotEmpty(S);
            testCase.verifyNotEmpty(X);

            testCase.verifyEqual(size(X,2), meta.N - p);
            testCase.verifyEqual(size(X,1), numel(S));

            testCase.verifyTrue(all(isfinite(S)), 'S contains NaN/Inf');
            testCase.verifyTrue(all(isfinite(X(:))), 'X contains NaN/Inf');

            x = lmodx(X, n);
            testCase.verifySize(x, [n, meta.N - p]);
            testCase.verifyTrue(all(isfinite(x(:))), 'x contains NaN/Inf');

            % Estimate LPV matrices
            [A, B, C, D, K] = lx2abcdk(x, u, y, mu, f, p);

            % With mu=[1 rho], s=2 and SISO, the matrices should be 1x2 (except C,D, padded)
            testCase.verifySize(A, [1 2]);
            testCase.verifySize(B, [1 2]);
            testCase.verifySize(C, [1 2]);
            testCase.verifySize(D, [1 2]);
            testCase.verifySize(K, [1 2]);

            testCase.verifyTrue(all(isfinite(A(:))));
            testCase.verifyTrue(all(isfinite(B(:))));
            testCase.verifyTrue(all(isfinite(C(:))));
            testCase.verifyTrue(all(isfinite(D(:))));
            testCase.verifyTrue(all(isfinite(K(:))));

            % Basic prediction check using constant C and D parts
            uTrim = u(p+1:p+size(x,2))';
            yTrim = y(p+1:p+size(x,2))';
            yHat = C(1) * x + D(1) * uTrim;
            
            err = yTrim - yHat;
            vaf = 100 * (1 - var(err,1) / var(yTrim, 1));

            % Loose threshold: this is just a sanity test
            testCase.verifyGreaterThan(vaf, 40);
        end
    end
end